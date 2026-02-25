from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask import render_template, request
import os
from app.src.logging_config import logger 
from flask_cors import CORS
from flask_migrate import Migrate
from datetime import datetime
import shutil

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'

def create_app():
    logger.info("Betting program started") 
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'super-secret-key'

    if os.environ.get("DOCKER") == "1":
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////instance/betting_model.db'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///betting_model.db'

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['DEBUG'] = True

    db.init_app(app)
    # migrate = Migrate(app, db)
    login_manager.init_app(app)
    CORS(app)

    from .src.models import User

    @login_manager.user_loader
    def load_user(user_id):
        logger.debug(f"load_user called with ID: {user_id}")
        return User.query.get(int(user_id))

    from . import routes
    app.register_blueprint(routes.bp)

    @app.errorhandler(500)
    def handle_internal_error(error):
        logger.error(f"HTTP 500 error: {error}")
        return render_template("500.html"), 500
    
    @app.errorhandler(404)
    def handle_not_found_error(error):
        logger.error(f"HTTP 500 error: {error}")
        return render_template("500.html"), 404

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        logger.critical(f"Unexpected critical error: {error}", exc_info=True)
        return render_template("500.html"), 500
    
    @app.before_request
    def log_request():
        logger.info(f"Request: {request.method} {request.path}")

    @app.after_request
    def log_response(response):
        logger.info(f"{request.method} {request.path} returned {response.status}")
        return response

    return app
import atexit

# Backup database and log exit
def log_backup_exit():
    logger.critical("Finance program exited unexpectedly or was terminated.")
    try:
        source = '../instance/finance.db'
        backup_dir = '../backups'
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = f"{backup_dir}/backup_{timestamp}.db"
        
        shutil.copy2(source, dest)
        logger.info(f"Database backed up to {dest}")
    except Exception as e:
        logger.error(f"Backup failed: {e}")

atexit.register(log_backup_exit)
