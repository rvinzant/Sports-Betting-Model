from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask import render_template, request
import os
from .logging_config import logger
from flask_cors import CORS
from app.utils import update_and_train, backup_db_and_logs

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'

def create_app(config_class=None):
    logger.info("Betting program started") 
    app = Flask(__name__)
    if config_class:
        app.config.from_object(config_class)
    else:
        app.config['SECRET_KEY'] = 'super-secret-key'

        if os.environ.get("DOCKER") == "1":
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////instance/betting_model.db'
        else:
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///betting_model.db'

        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['DEBUG'] = True
    with app.app_context():
        update_and_train()

    db.init_app(app)
    login_manager.init_app(app)
    CORS(app)

    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        logger.debug(f"load_user called with ID: {user_id}")
        return User.query.get(int(user_id))

    from . import routes
    app.register_blueprint(routes.bp)

    @app.errorhandler(500)
    def handle_internal_error(error):
        logger.error(f"HTTP 500 error: {error}")
        return render_template("error.html", number=500), 500
    
    @app.errorhandler(404)
    def handle_not_found_error(error):
        logger.error(f"HTTP 404 error: {error}")
        return render_template("error.html", number=404), 404

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        logger.critical(f"Unexpected critical error: {error}", exc_info=True)
        return render_template("error.html", number=error.code), 500
    
    @app.before_request
    def log_request():
        logger.info(f"Request: {request.method} {request.path}")

    @app.after_request
    def log_response(response):
        logger.info(f"{request.method} {request.path} returned {response.status}")
        return response

    return app


import atexit
def exitFunction():
    logger.critical("Betting program exited unexpectedly or was terminated.")
    backup_db_and_logs()
atexit.register(exitFunction)
