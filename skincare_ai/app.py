"""
AI SkinCare Analyzer – Flask Application Entry Point
Run: python app.py
"""

import os
from flask import Flask
from config import config
from database.db import init_app as init_db

# ── Blueprints ────────────────────────────────────────────────────────────────
from routes.auth_routes    import auth_bp
from routes.main_routes    import main_bp
from routes.analysis_routes import analysis_bp
from routes.product_routes import product_bp
from routes.chatbot_routes import chatbot_bp
from routes.history_routes import history_bp


def create_app(config_name: str = 'default') -> Flask:
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Init DB teardown
    init_db(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(history_bp)

    return app


if __name__ == '__main__':
    app = create_app('development')
    app.run(debug=True, host='0.0.0.0', port=5000)
