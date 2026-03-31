"""
app.py: This script acts as the "bridge." It will:
Listen for user requests on specific URLs (e.g., /predict).
Pass user input (like a team name) to your ML model.
Use render_template to send the prediction back to the HTML page.
"""

from app import create_app, db
from werkzeug.security import generate_password_hash
from app.logging_config import logger, file_handler


app = create_app()

# make file handler accessible from anywhere
app.config['FILE_HANDLER'] = file_handler

if __name__ == '__main__':
    logger.info("Starting Betting application")
    try:
        # Check installation of all parameters
        with app.app_context():
            db.create_all()
        host = "127.0.0.1"
        port = 8000
        print(f"Flask app is running at: http://{host}:{port}")
        app.run(debug=False, host=host, port=port, use_reloader=False)
    except Exception as e:
        logger.critical(f"Application crashed: {e}")
    finally:
        logger.info("Betting application stopped")