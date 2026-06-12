from flask import Blueprint, render_template, current_app, session, request, redirect, url_for, flash
from .models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from .logging_config import logger, savedLevel
from .utils import get_file_content, teams, roles_required, update_and_train, backup_db_and_logs, delete_old_backups, make_new_log_file, anonymous_required
from .predict import predictGame
import logging
import uuid

bp = Blueprint('main', __name__)
security_questions = ["What is your hometown?", "What was the name of your first pet?", "What is your mother's maiden name?"]


#-------------------------------
@bp.before_app_request
def ensure_session_id():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())


#-------------------------------
@bp.route('/')
def home():
    logger.debug(f"Home function used in routes.py Session ID: {session.get('session_id')}")
    return render_template('home.html')


#-------------------------------
@bp.route('/register', methods=['GET', 'POST'])
@anonymous_required
def register():
    logger.debug(f"Register function entered in routes.py method: {request.method} Session ID: {session.get('session_id')}")
    logger.info("Registration attempt initiated")
    if request.method == 'POST':
        email = request.form['email']
        nickname = request.form['nickname']
        password = request.form['password']
        answer1 = request.form['answer1']
        answer2 = request.form['answer2']
        answer3 = request.form['answer3']

        # Check for existing email and nickname
        if User.query.filter_by(email=email).first():
            logger.warning("Registration failed: Email already taken")
            logger.debug("Register function exited with failure in routes.py")
            flash("Email already taken!", "warning")
            return redirect(url_for('main.register'))

        if User.query.filter_by(nickname=nickname).first():
            logger.warning("Registration failed: Nickname already taken")
            logger.debug("Register function exited with failure in routes.py")
            flash("Nickname already taken!", "warning")
            return redirect(url_for('main.register'))

        # Hash password, add user data to db
        hashed_password = generate_password_hash(password)
        user = User(email=email, role="user", nickname=nickname, password=hashed_password, security_answers=[answer1, answer2, answer3])
        db.session.add(user)
        db.session.commit()
        logger.debug(f"User {nickname} registered in database")
        logger.info(f"New user registered: {nickname}")

        flash("Registration successful! Please login.", "success")
        logger.debug("Register function exited with success in routes.py")
        return redirect(url_for('main.login'))
    
    logger.debug(f"Register function exited from GET request in routes.py. Session ID: {session.get('session_id')}")
    return render_template('register.html', security_questions=security_questions)


#-------------------------------
@bp.route('/login', methods=['GET', 'POST'])
@anonymous_required
def login():
    logger.debug(f"Login function entered in routes.py method: {request.method} Session ID: {session.get('session_id')}")
    if request.method == 'POST':
        logger.info("Login attempt")
        logger.debug(f"Session ID: {session.get('session_id')}")
        identity = request.form['identity']
        password = request.form['password']

        user = User.query.filter((User.email == identity) | (User.nickname == identity)).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                logger.info(f"Authentication success for user: {user.nickname}")
                flash("Welcome back!", "success")
                logger.debug(f"Login function POST exited with success as user in routes.py. Session ID: {session.get('session_id')}")
                location = 'main.admin_dashboard' if user.role == 'admin' else 'main.dashboard'
                return redirect(url_for(location))
            else:
                logger.warning(f"Authentication failure for: {identity} (incorrect password)")
        else:
            logger.warning(f"Authentication failure for: {identity} (user not found)")
        flash("Invalid credentials, try again.", "warning")
        logger.debug(f"Login function POST exited with authentication failure in routes.py. Session ID: {session.get('session_id')}")
        return redirect(url_for('main.login'))

    logger.debug(f"Login function exited from GET request in routes.py. Session ID: {session.get('session_id')}")
    return render_template('login.html')


#-------------------------------
@bp.route('/login/security', methods=['GET', 'POST'])
@anonymous_required
def login_security():
    logger.debug(f"Login security function entered in routes.py method: {request.method} Session ID: {session.get('session_id')}")
    if request.method == 'POST':
        email = request.form['email']
        nickname = request.form['nickname']
        security_question = request.form['security_question']
        security_answer = request.form['security_answer']

        # Search for user info matching what was given
        user = User.query.filter_by(nickname=nickname, email=email).first()
        logger.debug(f"User found for security question: {user.nickname if user else 'None'}")
        
        # Check security question answer
        if user and user.security_answers[security_questions.index(security_question)].lower() == security_answer.lower():
            login_user(user)
            logger.info(f"Security question authentication success for user: {user.nickname}")
            flash("Welcome back! I reccomend changing your password.", "success")
            logger.debug(f"Login security function exited with success as user in routes.py. Session ID: {session.get('session_id')}")
            return redirect(url_for('main.profile'))
        else:
            logger.warning(f"Security question authentication failure for: {nickname} email: {email}")
            flash("Invalid credentials", "warning")
            logger.debug(f"Login security function exited with authentication failure in routes.py. Session ID: {session.get('session_id')}")
            return redirect(url_for('main.login_security'))

    logger.debug(f"Login security function exited from GET request in routes.py. Session ID: {session.get('session_id')}")
    return render_template('login_security.html', security_questions=security_questions)


#-------------------------------
@bp.route('/logout')
@login_required
def logout():
    logger.debug(f"Logout function entered in routes.py Session ID: {session.get('session_id')}")
    logger.info(f"User logged out: {current_user.nickname}")
    logout_user()
    flash("You have been logged out.", "info")
    logger.debug(f"Logout function exited in routes.py. Session ID: {session.get('session_id')}")
    return redirect(url_for('main.login'))


#-------------------------------
@bp.route('/dashboard')
def dashboard():
    logger.debug(f"Dashboard function entered in routes.py Session ID: {session.get('session_id')}")
    results = session.pop('prediction_results', None)
    prediction = None
    home = None
    away = None
    if results:
        prediction = results.get('prediction')
        home = results.get('home')
        away = results.get('away')
        logger.debug(f"Dashboard received prediction results from session: {results}")
    role = current_user.role if current_user.is_authenticated else None
    route = url_for('main.home')
    page = 'Home Page'
    if role == 'admin':
        route = url_for('main.admin_dashboard')
        page = 'Admin Dashboard'
    logger.debug(f"Dashboard function exited in routes.py. Session ID: {session.get('session_id')}")
    return render_template('dashboard.html', teams=teams, prediction=prediction, home=home, away=away, route=route, page=page)


#-------------------------------
@bp.route('/admin-dashboard')
@login_required
@roles_required('admin')
def admin_dashboard():
    logger.debug(f"Admin dashboard function used in routes.py Session ID: {session.get('session_id')}")
    return render_template('admin_dashboard.html')


#-------------------------------
@bp.route('/update-db', methods=['GET'])
@login_required
@roles_required('admin')
def update_db():
    logger.debug(f"Update_db function entered in routes.py Session ID: {session.get('session_id')}")
    result = update_and_train()
    if result:
        flash("Data updated and model trained successfully.", "success")
        logger.info("Data updated and model trained successfully.")
    else:
        flash("Failed to update and train model. Check logs for details.", "danger")
        logger.error("Failed to update and train model.")
    logger.debug(f"Update_db function exited in routes.py. Session ID: {session.get('session_id')}")
    return redirect(url_for('main.admin_dashboard'))


#-------------------------------
@bp.route('/backup-db-log', methods=['GET'])
@login_required
@roles_required('admin')
def admin_force_backup():
    logger.debug(f"admin_force_backup function entered in routes.py Session ID: {session.get('session_id')}")
    result = backup_db_and_logs()
    if result:
        flash("DB and logs backed up successfully", "success")
        logger.info("Backup successful.")
    else:
        flash("Failed to backup DB and log files. Check logs for details.", "danger")
        logger.error("Failed to backup.")
    logger.debug(f"admin_force_backup function exited in routes.py. Session ID: {session.get('session_id')}")
    return redirect(url_for('main.admin_dashboard'))


#-------------------------------
@bp.route('/clean-backups', methods=['GET'])
@login_required
@roles_required('admin')
def admin_clean_backups():
    logger.debug(f"admin_clean_backups function entered in routes.py Session ID: {session.get('session_id')}")
    result = delete_old_backups()
    if result:
        flash("Old backups deleted successfully", "success")
        logger.info("Backup clean successful.")
    else:
        flash("Failed to delete old backups. Check logs for details.", "danger")
        logger.error("Failed to clean backups.")
    logger.debug(f"admin_clean_backups function exited in routes.py. Session ID: {session.get('session_id')}")
    return redirect(url_for('main.admin_dashboard'))


#-------------------------------
@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    logger.debug(f"Profile function entered in routes.py with method: {request.method} Session ID: {session.get('session_id')}")

    if request.method == 'POST':
        email = request.form['email']
        nickname = request.form['nickname']
        new_pw = request.form['new_password']
        confirm_pw = request.form['confirm_password']

        # Check for email or nickname conflicts
        if email != current_user.email:
            if User.query.filter(User.email == email, User.id != current_user.id).first():
                logger.warning("Profile update failed: Email already taken")
                flash("Email already taken!", "warning")
                return redirect(url_for('main.profile'))

        if nickname != current_user.nickname:
            if User.query.filter(User.nickname == nickname, User.id != current_user.id).first():
                logger.warning(f"Profile update failed: Nickname \"{nickname}\" already taken")
                flash("Nickname already taken!", "warning")
                return redirect(url_for('main.profile'))
            
        # Check if user wants to change password
        if new_pw and confirm_pw:
            if new_pw == confirm_pw:
                current_user.password_hash = generate_password_hash(new_pw)
                logger.info(f"Password updated for user: {current_user.nickname}")
            else:
                flash("Passwords do not match!", "danger")
                return redirect(url_for('main.profile'))
        elif new_pw and not confirm_pw:
            logger.debug("No confirm password provided")
            flash("Please confirm your new password!", "warning")
            return redirect(url_for('main.profile'))

        # Update user info
        current_user.email = email
        current_user.nickname = nickname
        db.session.commit()
        logger.info(f"Profile updated for user: {current_user.nickname}")
        flash("Profile updated successfully!", "success")
        logger.debug(f"Profile function exited with success in routes.py. Session ID: {session.get('session_id')}")
        return redirect(url_for('main.profile'))
    
    # GET request handling
    userInfo = {'email': current_user.email, 'nickname': current_user.nickname}
    logger.debug(f"Profile function exited with GET request in routes.py. Session ID: {session.get('session_id')}")
    return render_template('profile.html', userInfo=userInfo)


#-------------------------------
@bp.route('/predict', methods=['POST'])
@login_required
def predict():
    logger.debug(f"Profile function entered in routes.py with method: {request.method} Session ID: {session.get('session_id')}")
    home = request.form['homeTeam']
    away = request.form['awayTeam']
    prediction = predictGame(home, away)
    session['prediction_results'] = {'prediction': prediction, 'home': home, 'away': away}
    
    logger.debug(f"Profile function exited in routes.py with method: {request.method}. Session ID: {session.get('session_id')}")
    return redirect(url_for('main.dashboard'))


logLevel = logging.DEBUG
#-------------------------------
# Used to change the log level at runtime from the logging info page
@bp.route('/logging-info', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def logging_info():
    logger.debug(f"logging_info function entered in routes.py method: {request.method} Session ID: {session.get('session_id')}")
    # Get the handler and check if its found
    file_handler = current_app.config.get('FILE_HANDLER')

    if not file_handler:
        logger.warning("Set log level function exited (handler not found)")
        logger.debug(f"logging_info function exited with failure in routes.py. Session ID: {session.get('session_id')}")
        flash("Log handler not found!", "warning")
        return redirect(url_for('main.admin_dashboard'))
    
    if request.method == 'POST':
        level = request.args.get('level').upper()

        levels = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING
        }

        if level not in levels:
            logger.warning(f"Set log level function exited (not valid level): {level}. Session ID: {session.get('session_id')}")
        else:
            file_handler.setLevel(levels[level])
            savedLevel("POST", level)
            flash(f"Log level changed to {level}", "info")
            logger.info(f"Log level changed to {level}")
            logger.debug(f"logging_info function exited with successin routes.py. Session ID: {session.get('session_id')}")
        return redirect(url_for('main.admin_dashboard'))
    
    log_file = get_file_content(directory='logs', filename='betting_model.log')
    content = log_file if log_file else "No log content found."
    logger.debug(f"Logging_info function exited with GET request in routes.py. Session ID: {session.get('session_id')}")
    return render_template('logging_info.html', current_level=savedLevel("GET", None), content=content)


#-------------------------------
# Used to force the creation of a new log file.
@bp.route('/force-new-log-file', methods=['GET'])
@login_required
@roles_required('admin')
def force_new_log_file():
    logger.debug(f"force_new_log_file function entered in routes.py Session ID: {session.get('session_id')}")
    result = make_new_log_file()
    if result:
        flash("New log file created successfully", "success")
        logger.info("New log file created successfully by admin.")
    else:
        flash("Failed to create new log file. Check logs for details.", "danger")
        logger.error("Admin route failed to create new log file.")
    logger.debug(f"force_new_log_file function exited in routes.py. Session ID: {session.get('session_id')}")
    return redirect(url_for('main.admin_dashboard'))