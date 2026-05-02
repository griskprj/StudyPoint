from flask import Flask
from config import Config
from app.extensions import db, migrate, jwt
from app import models

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from app.api.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    @app.route('/api/health')
    def health_check():
        return {'status': 'ok', 'message': 'StudyPoint API is running'}

    return app
