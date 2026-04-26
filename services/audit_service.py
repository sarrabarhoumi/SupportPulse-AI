from datetime import datetime
from services.db import get_db


def log_action(action, target_type, target_id=None, actor_id=None, severity='info', ip_address='', details=''):
    db = get_db()
    db.execute(
        """
        INSERT INTO audit_logs (actor_id, action, target_type, target_id, severity, ip_address, details, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (actor_id, action, target_type, target_id, severity, ip_address, details[:1000], datetime.utcnow().isoformat()),
    )
    db.commit()
