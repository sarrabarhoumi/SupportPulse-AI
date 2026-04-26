from functools import wraps
from datetime import datetime
from flask import g, session, redirect, url_for, flash, abort
from werkzeug.security import check_password_hash
from services.db import get_db
from services.audit_service import log_action


def load_current_user():
    user_id = session.get('user_id')
    g.current_user = None
    if not user_id:
        return
    g.current_user = get_db().execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()


def authenticate_user(email, password, ip_address=''):
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE email = ?', (email.lower(),)).fetchone()
    if not user:
        log_action('login_failed', 'auth', None, severity='security', ip_address=ip_address, details=email)
        return None
    if user['status'] != 'active' or not check_password_hash(user['password_hash'], password):
        log_action('login_failed', 'auth', user['id'], severity='security', ip_address=ip_address, details=email)
        return None
    now = datetime.utcnow().isoformat()
    db.execute('UPDATE users SET last_login_at = ?, updated_at = ? WHERE id = ?', (now, now, user['id']))
    db.commit()
    log_action('login_success', 'auth', user['id'], actor_id=user['id'], ip_address=ip_address)
    return user


def login_user(user):
    session.clear()
    session['user_id'] = user['id']


def logout_user(ip_address=''):
    user_id = session.get('user_id')
    if user_id:
        log_action('logout', 'auth', user_id, actor_id=user_id, ip_address=ip_address)
    session.clear()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get('user_id'):
            flash('Veuillez vous connecter pour accéder à cette page.', 'warning')
            return redirect(url_for('login'))
        return view(*args, **kwargs)
    return wrapped


def role_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            user = getattr(g, 'current_user', None)
            if not user:
                return redirect(url_for('login'))
            if user['role'] not in roles:
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return decorator
