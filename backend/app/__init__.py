from flask import Flask
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    @app.route('/api/health')
    def health_check():
        return {'status': 'ok', 'message': 'StudyPoint API is running'}

    return app
