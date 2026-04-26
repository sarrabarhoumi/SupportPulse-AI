from datetime import datetime
from services.db import get_db


def get_settings_map():
    rows = get_db().execute('SELECT setting_key, setting_value, description FROM settings ORDER BY setting_key').fetchall()
    return {row['setting_key']: {'value': row['setting_value'], 'description': row['description']} for row in rows}


def get_setting_value(key, default=''):
    row = get_db().execute('SELECT setting_value FROM settings WHERE setting_key = ?', (key,)).fetchone()
    return row['setting_value'] if row else default


def update_setting(key, value):
    db = get_db()
    db.execute(
        'UPDATE settings SET setting_value = ?, updated_at = ? WHERE setting_key = ?',
        (value[:500], datetime.utcnow().isoformat(), key),
    )
    db.commit()
