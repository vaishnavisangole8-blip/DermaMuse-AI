import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # ── Flask ──────────────────────────────────────────────
    SECRET_KEY = os.environ.get('SECRET_KEY', 'skincare_ai_secret_key_2024')
    DEBUG = False

    # ── Database ───────────────────────────────────────────
    MYSQL_HOST     = os.environ.get('MYSQL_HOST',     'localhost')
    MYSQL_USER     = os.environ.get('MYSQL_USER',     'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'vaishnavi@390')
    MYSQL_DB       = os.environ.get('MYSQL_DB',       'skincare_ai')
    MYSQL_PORT     = int(os.environ.get('MYSQL_PORT', 3306))

    # ── Upload ─────────────────────────────────────────────
    UPLOAD_FOLDER   = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024          # 10 MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

    # ── Session ────────────────────────────────────────────
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # ── AI Model ───────────────────────────────────────────
    MODEL_PATH = os.path.join(BASE_DIR, 'models', 'skin_model.h5')
    USE_MOCK_AI = True    # Set False when real trained model is available

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'default':     DevelopmentConfig
}
