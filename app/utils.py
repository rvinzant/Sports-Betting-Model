from .logging_config import logger
from functools import wraps
from flask import request, redirect, url_for, abort, session, flash
from flask_login import current_user
from datetime import datetime
import shutil
import os

teams = ["Atlanta Hawks","Boston Celtics","Brooklyn Nets",
    "Charlotte Hornets","Chicago Bulls","Cleveland Cavaliers",
    "Dallas Mavericks","Denver Nuggets","Detroit Pistons",
    "Golden State Warriors","Houston Rockets","Indiana Pacers",
    "LA Clippers","Los Angeles Lakers","Memphis Grizzlies",
    "Miami Heat","Milwaukee Bucks","Minnesota Timberwolves",
    "New Orleans Pelicans","New York Knicks","Oklahoma City Thunder",
    "Orlando Magic","Philadelphia 76ers","Phoenix Suns",
    "Portland Trail Blazers","Sacramento Kings","San Antonio Spurs",
    "Toronto Raptors","Utah Jazz","Washington Wizards"]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')


#-------------------------------
# Reads content of files and returns all characters.
def get_file_content(directory: str | None=BASE_DIR, filename: str | None=None):
    logger.debug(f"get_file_content function entered in utils.py for file: {directory+'/'+filename}. Session ID: {session.get('session_id')}")
    if filename is None:
        logger.warning("No filename given")
        logger.debug(f"get_file_content function exited with failure in utils.py. Session ID: {session.get('session_id')}")
        return "No filename given"
    file_path = os.path.join(directory, filename)
    try:
        with open(file_path, 'r') as f:
            logger.debug(f"get_file_content function exited with success in utils.py. Session ID: {session.get('session_id')}")
            return f.read()
    except FileNotFoundError:
        logger.warning(f"File not found: {file_path}")
        logger.debug(f"get_file_content function exited with failure in utils.py. Session ID: {session.get('session_id')}")
        return "File not found."
    except IOError as e:
        logger.warning(f"Error reading file: {e}")
        logger.debug(f"get_file_content function exited with failure in utils.py. Session ID: {session.get('session_id')}")
        return "Error reading file."
    

#-------------------------------
# Takes 2 teams as an input and returns an array of the averahe plus minus and pts from the last 5 games.
def getPreviousGameData(home_team, away_team):
    logger.debug(f"getPreviousGameData function entered in utils.py. Session ID: {session.get('session_id')}")
    from .data_loader import load_team_stats
    home_stats = load_team_stats(home_team)
    away_stats = load_team_stats(away_team)
    if home_stats.empty or away_stats.empty:
        logger.error("Could not find stats for one of the teams.")
        return None
    home_last_5_pts = home_stats["avg_points"].iloc[0]
    away_last_5_pts = away_stats["avg_points"].iloc[0]
    plus_minus_home = home_stats["avg_plus_minus"].iloc[0]
    plus_minus_away = away_stats["avg_plus_minus"].iloc[0]
    game_data = [home_last_5_pts, away_last_5_pts, plus_minus_home, plus_minus_away]
    logger.debug(f"getPreviousGameData function exited in utils.py. Session ID: {session.get('session_id')}")
    return game_data


#-------------------------------
# Updates game data and re-trains the model.
def update_and_train():
    logger.debug(f"Update_and_train function entered in utils.py")
    from .data_loader import update_nba_data
    from .train import trainModel
    try:
        update_nba_data()
        trainModel()
    except Exception as e:
        logger.error(f"Error occurred while updating data and training model: {e}")
        logger.debug("Update_and_train function exited with failure in utils.py")
        return False
    logger.debug(f"Update_and_train function exited with success in utils.py")
    return True

#-------------------------------
# Helper function to perform backup
def doBackup(source, dir, filetype):
    os.makedirs(dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = f"{dir}/backup_{timestamp}.{filetype}"
    shutil.copy2(source, dest)
    logger.info(f"{filetype} backed up to {dest}")


#-------------------------------
# Saves current db and log files to backups folder.
def backup_db_and_logs():
    logger.debug(f"backup_db_and_logs entered in utils.py")
    source1 = os.path.join(BASE_DIR, 'instance', 'betting_model.db')
    source2 = os.path.join(BASE_DIR, 'logs', 'betting_model.log')
    db_backup_dir = os.path.join(BACKUP_DIR, 'instance')
    log_backup_dir = os.path.join(BACKUP_DIR, 'logs')
    try:
        doBackup(source1, db_backup_dir, 'db')
        doBackup(source2, log_backup_dir, 'log')
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        return False
    logger.debug(f"backup_db_and_logs exited in utils.py")
    return True


#-------------------------------
# Deletes backup files older than date specified.
def delete_old_backups():
    logger.debug(f"Delete_old_backups function entered in utils.py Session ID: {session.get('session_id')}")
    log_dir = os.path.join(BACKUP_DIR, "logs")
    db_dir = os.path.join(BACKUP_DIR, "instance")
    def doDelete(dir, days: int | None=20):
        if os.path.exists(dir):
            for file in os.listdir(dir):
                date = datetime.strptime(file.split('_')[1], "%Y%m%d")
                if (datetime.now() - date).days > days:
                    delete_file(directory=dir, file_name=file)
    try:
        doDelete(log_dir)
        doDelete(db_dir)
    except Exception as e:
        logger.error(f"Error deleting old backups: {e}")
        logger.debug("Delete_old_backups function exited with failure in utils.py")
        return False
    logger.debug(f"Delete_old_backups function exited with success in utils.py. Session ID: {session.get('session_id')}")
    return True


#-------------------------------
# This takes a directory and filename as inputs and deletes the file if it exists.
def delete_file(directory: str | None=None, file_name: str | None=None):
    logger.debug(f"delete_file function entered in utils.py Session ID: {session.get('session_id')}")
    if directory is None or file_name is None:
        logger.debug("Delete_file exited because None type in utils.py")
        return
    file_path = os.path.join(directory, file_name)
    if os.path.exists(file_path):
        os.remove(file_path)
        logger.info(f"File at '{file_path}' deleted successfully.")
    else:
        logger.info(f"File at '{file_path}' does not exist.")
    logger.debug(f"delete_file function exited in utils.py. Session ID: {session.get('session_id')}")


#-------------------------------
# Creates a new log file and backs up the old one
def make_new_log_file():
    logger.debug(f"make_new_log_file function entered in utils.py Session ID: {session.get('session_id')}")
    log_dir = os.path.join(BASE_DIR, "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "betting_model.log")
    if os.path.exists(log_file):
        doBackup(log_file, os.path.join(BACKUP_DIR, "logs"), "log")
        logger.info("Old log file backed up successfully.")
    try:
        with open(log_file, 'w') as f:
            f.write(f"New log file created at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    except Exception as e:
        logger.error(f"Failed to create new log file: {e}")
        logger.debug(f"make_new_log_file function exited with failure in utils.py. Session ID: {session.get('session_id')}")
        return False
    logger.debug(f"make_new_log_file function exited with success in utils.py. Session ID: {session.get('session_id')}")
    return True


#-------------------------------
# Takes a tuple of roles as an input. Checks that a user has a necessary role.
def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                logger.warning(f"Unauthenticated access attempt to {request.path}")
                return redirect(url_for('main.login'))
                
            if current_user.role not in roles:
                logger.warning(f"Forbidden access attempt by {current_user.nickname} to {request.path}")
                abort(403)
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator


#-------------------------------
# Decorator to restrict access to routes for authenticated users
def anonymous_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            flash("You cannot access this page while logged in.", "warning")
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function