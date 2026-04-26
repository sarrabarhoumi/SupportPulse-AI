import csv
import json
import os
import sqlite3
import sys
from datetime import datetime

from werkzeug.security import generate_password_hash

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from config import DATABASE_PATH, DEFAULT_ADMIN_EMAIL, DEFAULT_ADMIN_PASSWORD
from services.scoring_engine import SCORER

SCHEMA_PATH = os.path.join(BASE_DIR, 'database', 'schema.sql')
CSV_PATH = os.path.join(BASE_DIR, 'data', 'demo_tickets.csv')
JSON_PATH = os.path.join(BASE_DIR, 'data', 'demo_tickets.json')


def _next_reference(conn):
    total = conn.execute('SELECT COUNT(*) FROM tickets').fetchone()[0] + 1
    return f'SP-{total:05d}'


def init_database():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)
    with sqlite3.connect(DATABASE_PATH) as conn:
        with open(SCHEMA_PATH, 'r', encoding='utf-8') as handle:
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


def _insert_ticket(conn, row):
    now = datetime.utcnow().isoformat()
    result = SCORER.analyze(row.get('subject', ''), row.get('content', ''), row.get('customer_email', ''))
    cursor = conn.execute(
        """
        INSERT INTO tickets (
            reference_code, source, subject, customer_name, customer_email, channel, content, language,
            status, predicted_category, predicted_priority, predicted_urgency, predicted_sentiment,
            confidence_score, summary, suggested_team, explanation, processing_time_ms, created_by, created_at, updated_at
        ) VALUES (?, 'import', ?, ?, ?, ?, ?, 'fr', 'analyzed', ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
        """,
        (
            _next_reference(conn),
            row.get('subject', '').strip(),
            row.get('customer_name', '').strip(),
            row.get('customer_email', '').strip().lower(),
            (row.get('channel', 'email') or 'email').strip(),
            row.get('content', '').strip(),
            result['category'], result['priority'], result['urgency'], result['sentiment'], result['confidence_score'],
            result['summary'], result['suggested_team'], result['explanation'], result['processing_time_ms'], now, now,
        ),
    )
    prediction_id = conn.execute(
        """
        INSERT INTO ticket_predictions (
            ticket_id, category_name, priority_name, urgency_name, sentiment, confidence_score,
            summary, suggested_team, explanation, reasons_json, engine_version, processed_by, processed_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
        """,
        (
            cursor.lastrowid, result['category'], result['priority'], result['urgency'], result['sentiment'],
            result['confidence_score'], result['summary'], result['suggested_team'], result['explanation'],
            json.dumps(result['reasons'], ensure_ascii=False), result['engine_version'], now,
        ),
    ).lastrowid
    conn.execute('UPDATE tickets SET latest_prediction_id = ? WHERE id = ?', (prediction_id, cursor.lastrowid))


def seed_demo_tickets():
    with sqlite3.connect(DATABASE_PATH) as conn:
        with open(CSV_PATH, 'r', encoding='utf-8') as handle:
            for row in csv.DictReader(handle):
                _insert_ticket(conn, row)
        with open(JSON_PATH, 'r', encoding='utf-8') as handle:
            for row in json.load(handle):
                _insert_ticket(conn, row)
        conn.commit()


if __name__ == '__main__':
    init_database()
    seed_demo_tickets()
    print('Base SQLite initialisée avec succès.')
