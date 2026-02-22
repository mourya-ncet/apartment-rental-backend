from flask import Flask
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from .config import Config

jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    jwt.init_app(app)

    # Explicit Swagger config
    template = {
        "swagger": "2.0",
        "info": {
            "title": "Apartment Management API",
            "description": "API documentation for Apartment Rental Backend",
            "version": "1.0"
        }
    }

    Swagger(app, template=template)

    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.admin import admin_bp
    from .routes.user import user_bp
    from .routes.reports import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(reports_bp)

    return app
