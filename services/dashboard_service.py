from services.db import get_db
from services.settings_service import get_setting_value


def _count(query, params=()):
    row = get_db().execute(query, params).fetchone()
    return row[0] if row else 0


def get_dashboard_metrics():
    db = get_db()
    metrics = {
        'total_tickets': _count('SELECT COUNT(*) FROM tickets'),
        'urgent_tickets': _count("SELECT COUNT(*) FROM tickets WHERE predicted_urgency = 'elevee'"),
        'critical_tickets': _count("SELECT COUNT(*) FROM tickets WHERE predicted_priority = 'critique'"),
        'average_processing_time': round(_count('SELECT COALESCE(AVG(processing_time_ms), 0) FROM tickets'), 1),
        'default_processing_minutes': get_setting_value('default_processing_minutes', '42'),
    }
    metrics['by_category'] = db.execute('SELECT predicted_category AS label, COUNT(*) AS total FROM tickets GROUP BY predicted_category ORDER BY total DESC').fetchall()
    metrics['by_priority'] = db.execute('SELECT predicted_priority AS label, COUNT(*) AS total FROM tickets GROUP BY predicted_priority ORDER BY total DESC').fetchall()
    metrics['recent_activity'] = db.execute('SELECT * FROM tickets ORDER BY updated_at DESC LIMIT 8').fetchall()
    return metrics


def get_statistics_payload():
    db = get_db()
    return {
        'tickets_by_day': db.execute("SELECT substr(created_at, 1, 10) AS day, COUNT(*) AS total FROM tickets GROUP BY substr(created_at, 1, 10) ORDER BY day").fetchall(),
        'categories': db.execute('SELECT predicted_category AS label, COUNT(*) AS total FROM tickets GROUP BY predicted_category ORDER BY total DESC').fetchall(),
        'priorities': db.execute('SELECT predicted_priority AS label, COUNT(*) AS total FROM tickets GROUP BY predicted_priority ORDER BY total DESC').fetchall(),
        'channels': db.execute('SELECT channel AS label, COUNT(*) AS total FROM tickets GROUP BY channel ORDER BY total DESC').fetchall(),
        'imports': db.execute('SELECT * FROM imports ORDER BY created_at DESC LIMIT 10').fetchall(),
    }
