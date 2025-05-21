# app/__init__.py
from flask import Flask
from dotenv import load_dotenv
import os
from flask_login import LoginManager
from app.user import User

login_manager = LoginManager()
login_manager.login_view = "auth.login"


def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY")

    from .routes import main
    from .auth import auth
    from .ai_agent import ai_bp

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(ai_bp)

    # Init login manager
    login_manager.init_app(app)

    # Tell Flask-Login how to load a user
    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(user_id)

    return app
