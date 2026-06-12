"""
app.py: This script acts as the "bridge." It will:
Listen for user requests on specific URLs (e.g., /predict).
Pass user input (like a team name) to your ML model.
Use render_template to send the prediction back to the HTML page.
"""

import os
from app import create_app, db
from werkzeug.security import generate_password_hash
from app.logging_config import logger, file_handler
from app.models import User


app = create_app()
app.config['FILE_HANDLER'] = file_handler

#------------------------------
# Add a default admin user if it doesn't exist
def addAdmin():
    admin_exists = User.query.filter_by(role='admin').first() 
    if not admin_exists:
        hashed_password = generate_password_hash("admin123")
        admin = User(
            nickname="admin", 
            email="admin@example.com", 
            password=hashed_password, 
            role="admin",
            security_answers=[1,1,1]
        )
        db.session.add(admin)
        db.session.commit()
        logger.info("Default admin user created successfully.")


#------------------------------
if __name__ == '__main__':
    logger.info("Starting Betting application")
    if os.environ.get("DOCKER") == "1":
        host = "0.0.0.0"
    else:
        host = "127.0.0.1"
    try:
        with app.app_context():
            db.create_all()
            addAdmin()
        port = 5050
        print(f"Flask app is running at: http://127.0.0.1:{port}")
        app.run(debug=False, host=host, port=port, use_reloader=False)
    except Exception as e:
        logger.critical(f"Application crashed: {e}")
    finally:
        logger.info("Betting application stopped")