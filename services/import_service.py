import csv
import io
import json
from datetime import datetime
from config import ALLOWED_IMPORT_EXTENSIONS
from services.db import get_db
from services.ticket_service import create_and_analyze_ticket


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMPORT_EXTENSIONS


def _parse_csv(stream):
    text = stream.read().decode('utf-8')
    return list(csv.DictReader(io.StringIO(text)))


def _parse_json(stream):
    text = stream.read().decode('utf-8')
    data = json.loads(text)
    return data if isinstance(data, list) else []


def import_tickets_from_file(uploaded_file, user_id):
    extension = uploaded_file.filename.rsplit('.', 1)[1].lower()
    rows = _parse_csv(uploaded_file.stream) if extension == 'csv' else _parse_json(uploaded_file.stream)
    imported = 0
    failed = 0
    errors = []
    for row in rows:
        subject = (row.get('subject') or '').strip()
        content = (row.get('content') or '').strip()
        if not subject or not content:
            failed += 1
            errors.append('Ligne ignorée : sujet ou contenu manquant.')
            continue
        payload = {
            'subject': subject[:255],
            'customer_name': (row.get('customer_name') or '')[:120],
            'customer_email': (row.get('customer_email') or '')[:255].lower(),
            'channel': (row.get('channel') or 'email')[:30],
            'content': content[:4000],
            'language': 'fr',
        }
        create_and_analyze_ticket(payload, created_by=user_id, source='import')
        imported += 1
    db = get_db()
    db.execute(
        'INSERT INTO imports (file_name, import_type, imported_count, failed_count, created_by, created_at) VALUES (?, ?, ?, ?, ?, ?)',
        (uploaded_file.filename, extension, imported, failed, user_id, datetime.utcnow().isoformat()),
    )
    db.commit()
    return {'imported_count': imported, 'failed_count': failed, 'errors': errors}
