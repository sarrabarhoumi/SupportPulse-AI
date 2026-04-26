import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'storage', 'supportpulse.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
LOG_PATH = os.path.join(BASE_DIR, 'logs', 'app.log')
DATA_DIR = os.path.join(BASE_DIR, 'data')
MAX_CONTENT_LENGTH = 2 * 1024 * 1024
ALLOWED_IMPORT_EXTENSIONS = {'csv', 'json'}
SECRET_KEY = os.environ.get('SUPPORTPULSE_SECRET_KEY', 'supportpulse-demo-secret-key')
DEFAULT_ADMIN_EMAIL = 'admin@supportpulse.local'
DEFAULT_ADMIN_PASSWORD = 'Admin123!'
APP_NAME = 'SupportPulse AI'
ENGINE_VERSION = '1.0.0-hybrid-fr'
