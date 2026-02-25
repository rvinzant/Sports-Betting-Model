"""
app.py: This script acts as the "bridge." It will:
Listen for user requests on specific URLs (e.g., /predict).
Pass user input (like a team name) to your ML model.
Use render_template to send the prediction back to the HTML page.
"""

from app import create_app, db
# from app.src.models import User
from werkzeug.security import generate_password_hash
from app.src.logging_config import logger, file_handler
import subprocess
import os


app = create_app()

# make file handler accessible from anywhere
app.config['FILE_HANDLER'] = file_handler        

"""
# to run: "flask update_db"
@app.cli.command("update_db")
def update_db():
    # "flask db stamp head" to assume db up to date
    # check for migrations folder
    migrations_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'migrations')

    # create migrations folder if it doesn't exist
    if not os.path.exists(migrations_path):
        logger.info("Migrations folder not found, initializing migrations.")
        output = subprocess.run(["flask", "db", "init"], capture_output=True, text=True)
        logger.info(f"Init migrations code: {output.returncode} output: {output.stdout}")
        if output.returncode != 0:
            logger.error(f"Init migrations error: {output.stderr}")
            return
        
    # get user input for migration message
    userInput = input("What's your message?")
    logger.info(f"User message: {userInput}")
    # migrate and upgrade
    output1 = subprocess.run(["flask", "db", "migrate", "-m", userInput], capture_output=True, text=True)
    logger.info(f"Migration code: {output1.returncode} output: {output1.stdout}")

    if output1.returncode != 0:
        logger.error(f"Migration error: {output1.stderr}")
    else:
        output2 = subprocess.run(["flask", "db", "upgrade"], capture_output=True, text=True)
        logger.info(f"Upgrade code: {output2.returncode} output: {output2.stdout}")
        if output2.returncode != 0:
            logger.error(f"Upgrade error: {output2.stderr}")
    return
"""

if __name__ == '__main__':
    logger.info("Starting Finance application")
    try:
        # Check installation of all parameters
        with app.app_context():
            db.create_all()
        host = "127.0.0.1"
        port = 5050
        print(f"Flask app is running at: http://{host}:{port}")
        app.run(debug=False, host=host, port=port, use_reloader=False)
    except Exception as e:
        logger.critical(f"Application crashed: {e}")
    finally:
        logger.info("Finance application stopped")