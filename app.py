import os
import secrets
import sqlite3
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, abort, g
from werkzeug.security import generate_password_hash

from config import SECRET_KEY, DATABASE_PATH, MAX_CONTENT_LENGTH, UPLOAD_FOLDER, DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_PASSWORD
from services.auth_service import authenticate_user, login_user, logout_user, login_required, role_required, load_current_user
from services.audit_service import log_action
from services.dashboard_service import get_dashboard_metrics, get_statistics_payload
from services.db import close_db, get_db
from services.import_service import allowed_file, import_tickets_from_file
from services.settings_service import get_settings_map, update_setting
from services.ticket_service import analyze_ticket, apply_correction, create_and_analyze_ticket, get_ticket, list_tickets
from services.scoring_engine import SCORER

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def init_database_if_needed():
    if os.path.exists(DATABASE_PATH):
        return
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    with sqlite3.connect(DATABASE_PATH) as conn:
        schema_path = os.path.join(os.path.dirname(__file__), 'database', 'schema.sql')
        with open(schema_path, 'r', encoding='utf-8') as handle:
            conn.executescript(handle.read())
        now = datetime.utcnow().isoformat()
        users = [
            ('Admin SupportPulse', DEFAULT_ADMIN_EMAIL, generate_password_hash(DEFAULT_ADMIN_PASSWORD), 'admin', 'active', now, now),
            ('Analyste Demo', 'analyste@supportpulse.local', generate_password_hash('Analyst123!'), 'analyst', 'active', now, now),
            ('Lecteur Demo', 'viewer@supportpulse.local', generate_password_hash('Viewer123!'), 'viewer', 'active', now, now),
        ]
        conn.executemany(
            'INSERT INTO users (full_name, email, password_hash, role, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
            users,
        )
        conn.commit()
    from scripts.init_db import seed_demo_tickets
    seed_demo_tickets()


@app.before_request
def before_request():
    init_database_if_needed()
    load_current_user()
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(16)


@app.teardown_appcontext
def teardown(_error):
    close_db(_error)


@app.context_processor
def inject_globals():
    return {'csrf_token': session.get('csrf_token', ''), 'current_user': getattr(g, 'current_user', None), 'app_name': 'SupportPulse AI'}


@app.template_filter('datetime_fr')
def datetime_fr(value):
    if not value:
        return '-'
    return value.replace('T', ' ')[:16]


def validate_csrf():
    token = request.form.get('csrf_token', '')
    if not token or token != session.get('csrf_token'):
        abort(400, description='Jeton CSRF invalide.')


def sanitize_form_value(field_name, required=True, max_length=255):
    value = (request.form.get(field_name) or '').strip()
    if required and not value:
        raise ValueError(f"Le champ '{field_name}' est obligatoire.")
    return value[:max_length]


@app.route('/')
def home():
    if session.get('user_id'):
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        validate_csrf()
        email = (request.form.get('email') or '').strip().lower()
        password = request.form.get('password') or ''
        user = authenticate_user(email, password, request.remote_addr or '')
        if user:
            login_user(user)
            session['csrf_token'] = secrets.token_hex(16)
            flash('Connexion réussie.', 'success')
            return redirect(url_for('dashboard'))
        flash('Identifiants invalides ou compte inactif.', 'danger')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user(request.remote_addr or '')
    flash('Déconnexion effectuée.', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    metrics = get_dashboard_metrics()
    return render_template('dashboard.html', metrics=metrics)


@app.route('/tickets')
@login_required
def tickets_list():
    filters = {
        'search': (request.args.get('search') or '').strip(),
        'category': (request.args.get('category') or '').strip(),
        'priority': (request.args.get('priority') or '').strip(),
        'status': (request.args.get('status') or '').strip(),
    }
    tickets = list_tickets(**filters)
    categories = get_db().execute('SELECT name FROM categories WHERE active = 1 ORDER BY name').fetchall()
    return render_template('tickets/list.html', tickets=tickets, filters=filters, categories=categories)


@app.route('/tickets/add', methods=['GET', 'POST'])
@login_required
def tickets_add():
    if request.method == 'POST':
        validate_csrf()
        try:
            payload = {
                'subject': sanitize_form_value('subject'),
                'customer_name': sanitize_form_value('customer_name', required=False, max_length=120),
                'customer_email': sanitize_form_value('customer_email', required=False),
                'channel': sanitize_form_value('channel', required=True, max_length=30),
                'content': sanitize_form_value('content', required=True, max_length=4000),
                'language': 'fr',
            }
            ticket_id = create_and_analyze_ticket(payload, created_by=session.get('user_id'), source='manual')
            log_action('ticket_created', 'ticket', ticket_id, actor_id=session.get('user_id'), ip_address=request.remote_addr or '', details=payload['subject'])
            flash('Ticket créé et analysé avec succès.', 'success')
            return redirect(url_for('ticket_detail', ticket_id=ticket_id))
        except ValueError as exc:
            flash(str(exc), 'danger')
    return render_template('tickets/add.html')


@app.route('/tickets/import', methods=['GET', 'POST'])
@login_required
def tickets_import():
    result = None
    if request.method == 'POST':
        validate_csrf()
        uploaded_file = request.files.get('import_file')
        if not uploaded_file or not uploaded_file.filename:
            flash('Veuillez sélectionner un fichier CSV ou JSON.', 'danger')
        elif not allowed_file(uploaded_file.filename):
            flash('Format non autorisé. Utilisez CSV ou JSON.', 'danger')
        else:
            result = import_tickets_from_file(uploaded_file, session.get('user_id'))
            log_action('tickets_imported', 'import', None, actor_id=session.get('user_id'), ip_address=request.remote_addr or '', details=str(result))
            flash(f"Import terminé : {result['imported_count']} ticket(s) importé(s), {result['failed_count']} échec(s).", 'success')
    return render_template('tickets/import.html', result=result)


@app.route('/tickets/<int:ticket_id>')
@login_required
def ticket_detail(ticket_id):
    ticket = get_ticket(ticket_id)
    if not ticket:
        abort(404)
    categories = get_db().execute('SELECT name FROM categories WHERE active = 1 ORDER BY name').fetchall()
    return render_template('tickets/detail.html', ticket=ticket, categories=categories)


@app.route('/tickets/<int:ticket_id>/reanalyze', methods=['POST'])
@login_required
def ticket_reanalyze(ticket_id):
    validate_csrf()
    analyze_ticket(ticket_id, processed_by=session.get('user_id'))
    log_action('ticket_reanalyzed', 'ticket', ticket_id, actor_id=session.get('user_id'), ip_address=request.remote_addr or '')
    flash('Ticket réanalysé avec succès.', 'success')
    return redirect(url_for('ticket_detail', ticket_id=ticket_id))


@app.route('/tickets/<int:ticket_id>/correct', methods=['POST'])
@login_required
def ticket_correct(ticket_id):
    validate_csrf()
    payload = {
        'new_category': sanitize_form_value('new_category'),
        'new_priority': sanitize_form_value('new_priority'),
        'new_urgency': sanitize_form_value('new_urgency'),
        'comment': sanitize_form_value('comment', required=False, max_length=500),
    }
    apply_correction(ticket_id, payload, session.get('user_id'))
    log_action('ticket_corrected', 'ticket', ticket_id, actor_id=session.get('user_id'), ip_address=request.remote_addr or '', details=str(payload))
    flash('Correction enregistrée.', 'success')
    return redirect(url_for('ticket_detail', ticket_id=ticket_id))


@app.route('/stats')
@login_required
def stats():
    return render_template('stats.html', stats=get_statistics_payload())


@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_users():
    db = get_db()
    if request.method == 'POST':
        validate_csrf()
        try:
            full_name = sanitize_form_value('full_name')
            email = sanitize_form_value('email').lower()
            password = sanitize_form_value('password')
            role = sanitize_form_value('role')
            now = datetime.utcnow().isoformat()
            db.execute(
                """
                INSERT INTO users (full_name, email, password_hash, role, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, 'active', ?, ?)
                """,
                (full_name, email, generate_password_hash(password), role, now, now),
            )
            db.commit()
            log_action('user_created', 'user', None, actor_id=session.get('user_id'), ip_address=request.remote_addr or '', details=email)
            flash('Utilisateur créé.', 'success')
            return redirect(url_for('admin_users'))
        except sqlite3.IntegrityError:
            flash('Un utilisateur avec cet email existe déjà.', 'danger')
        except ValueError as exc:
            flash(str(exc), 'danger')
    users = db.execute('SELECT * FROM users ORDER BY created_at DESC').fetchall()
    return render_template('admin/users.html', users=users)


@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_settings():
    if request.method == 'POST':
        validate_csrf()
        for key in ['critical_keywords', 'vip_domains', 'confidence_threshold', 'default_processing_minutes', 'engine_version']:
            if key in request.form:
                update_setting(key, request.form.get(key, '').strip())
        log_action('settings_updated', 'settings', None, actor_id=session.get('user_id'), ip_address=request.remote_addr or '')
        flash('Paramètres mis à jour.', 'success')
        return redirect(url_for('admin_settings'))
    return render_template('admin/settings.html', settings=get_settings_map())


@app.route('/admin/logs')
@login_required
@role_required('admin')
def admin_logs():
    logs = get_db().execute(
        """
        SELECT a.*, u.full_name AS actor_name
        FROM audit_logs a
        LEFT JOIN users u ON u.id = a.actor_id
        ORDER BY a.created_at DESC LIMIT 100
        """
    ).fetchall()
    return render_template('admin/logs.html', logs=logs)


@app.route('/api/analyze-preview', methods=['POST'])
@login_required
def analyze_preview():
    payload = request.get_json(silent=True) or {}
    subject = (payload.get('subject') or '').strip()[:255]
    content = (payload.get('content') or '').strip()[:4000]
    customer_email = (payload.get('customer_email') or '').strip()[:255]
    if not subject or not content:
        return jsonify({'error': 'Sujet et contenu requis.'}), 400
    return jsonify(SCORER.analyze(subject, content, customer_email))


@app.errorhandler(400)
def handle_bad_request(error):
    return render_template('error.html', code=400, message=str(error.description)), 400


@app.errorhandler(403)
def handle_forbidden(_error):
    return render_template('error.html', code=403, message='Accès refusé.'), 403


@app.errorhandler(404)
def handle_not_found(_error):
    return render_template('error.html', code=404, message='Ressource introuvable.'), 404


@app.errorhandler(413)
def handle_too_large(_error):
    flash('Fichier trop volumineux. Limite fixée à 2 Mo.', 'danger')
    return redirect(request.referrer or url_for('tickets_import'))


if __name__ == '__main__':
    init_database_if_needed()
    app.run(debug=True)
