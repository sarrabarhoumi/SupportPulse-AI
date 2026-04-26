import json
from datetime import datetime
from services.db import get_db
from services.scoring_engine import SCORER


def _next_reference(db):
    total = db.execute('SELECT COUNT(*) AS total FROM tickets').fetchone()['total'] + 1
    return f'SP-{total:05d}'


def create_ticket(payload, created_by=None, source='manual'):
    db = get_db()
    now = datetime.utcnow().isoformat()
    cursor = db.execute(
        """
        INSERT INTO tickets (
            reference_code, source, subject, customer_name, customer_email, channel, content, language,
            status, created_by, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'new', ?, ?, ?)
        """,
        (
            _next_reference(db), source, payload['subject'], payload.get('customer_name', ''), payload.get('customer_email', ''),
            payload.get('channel', 'email'), payload['content'], payload.get('language', 'fr'), created_by, now, now,
        ),
    )
    db.commit()
    return cursor.lastrowid


def analyze_ticket(ticket_id, processed_by=None):
    db = get_db()
    ticket = db.execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,)).fetchone()
    if not ticket:
        return None
    result = SCORER.analyze(ticket['subject'], ticket['content'], ticket['customer_email'] or '')
    now = datetime.utcnow().isoformat()
    cursor = db.execute(
        """
        INSERT INTO ticket_predictions (
            ticket_id, category_name, priority_name, urgency_name, sentiment, confidence_score,
            summary, suggested_team, explanation, reasons_json, engine_version, processed_by, processed_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            ticket_id, result['category'], result['priority'], result['urgency'], result['sentiment'], result['confidence_score'],
            result['summary'], result['suggested_team'], result['explanation'], json.dumps(result['reasons'], ensure_ascii=False),
            result['engine_version'], processed_by, now,
        ),
    )
    prediction_id = cursor.lastrowid
    db.execute(
        """
        UPDATE tickets SET
            status = 'analyzed',
            predicted_category = ?,
            predicted_priority = ?,
            predicted_urgency = ?,
            predicted_sentiment = ?,
            confidence_score = ?,
            summary = ?,
            suggested_team = ?,
            explanation = ?,
            processing_time_ms = ?,
            latest_prediction_id = ?,
            updated_at = ?
        WHERE id = ?
        """,
        (
            result['category'], result['priority'], result['urgency'], result['sentiment'], result['confidence_score'],
            result['summary'], result['suggested_team'], result['explanation'], result['processing_time_ms'], prediction_id, now, ticket_id,
        ),
    )
    db.commit()
    return result


def create_and_analyze_ticket(payload, created_by=None, source='manual'):
    ticket_id = create_ticket(payload, created_by=created_by, source=source)
    analyze_ticket(ticket_id, processed_by=created_by)
    return ticket_id


def list_tickets(search='', category='', priority='', status=''):
    db = get_db()
    query = """
        SELECT t.* FROM tickets t
        WHERE 1 = 1
    """
    params = []
    if search:
        query += ' AND (t.reference_code LIKE ? OR t.subject LIKE ? OR t.content LIKE ? OR t.customer_email LIKE ?)'
        like = f'%{search}%'
        params.extend([like, like, like, like])
    if category:
        query += ' AND t.predicted_category = ?'
        params.append(category)
    if priority:
        query += ' AND t.predicted_priority = ?'
        params.append(priority)
    if status:
        query += ' AND t.status = ?'
        params.append(status)
    query += ' ORDER BY t.created_at DESC'
    return db.execute(query, params).fetchall()


def get_ticket(ticket_id):
    db = get_db()
    ticket = db.execute(
        """
        SELECT t.*, u.full_name AS creator_name
        FROM tickets t
        LEFT JOIN users u ON u.id = t.created_by
        WHERE t.id = ?
        """,
        (ticket_id,),
    ).fetchone()
    if not ticket:
        return None
    prediction = db.execute(
        'SELECT * FROM ticket_predictions WHERE ticket_id = ? ORDER BY processed_at DESC LIMIT 1',
        (ticket_id,),
    ).fetchone()
    if prediction:
        prediction = dict(prediction)
        try:
            prediction['reasons'] = json.loads(prediction.get('reasons_json') or '[]')
        except json.JSONDecodeError:
            prediction['reasons'] = []
    corrections = db.execute(
        """
        SELECT c.*, u.full_name AS corrected_by_name
        FROM ticket_corrections c
        LEFT JOIN users u ON u.id = c.corrected_by
        WHERE c.ticket_id = ?
        ORDER BY c.corrected_at DESC
        """,
        (ticket_id,),
    ).fetchall()
    return {'ticket': ticket, 'prediction': prediction, 'corrections': corrections}


def apply_correction(ticket_id, payload, corrected_by):
    db = get_db()
    ticket = db.execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,)).fetchone()
    if not ticket:
        return
    now = datetime.utcnow().isoformat()
    db.execute(
        """
        INSERT INTO ticket_corrections (
            ticket_id, previous_category, previous_priority, previous_urgency,
            new_category, new_priority, new_urgency, comment, corrected_by, corrected_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            ticket_id, ticket['predicted_category'], ticket['predicted_priority'], ticket['predicted_urgency'],
            payload['new_category'], payload['new_priority'], payload['new_urgency'], payload.get('comment', ''), corrected_by, now,
        ),
    )
    db.execute(
        """
        UPDATE tickets SET predicted_category = ?, predicted_priority = ?, predicted_urgency = ?, status = 'reviewed', updated_at = ?
        WHERE id = ?
        """,
        (payload['new_category'], payload['new_priority'], payload['new_urgency'], now, ticket_id),
    )
    db.commit()
