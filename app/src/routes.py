from flask import Blueprint, render_template, current_app, session, request, redirect, url_for, flash
from .models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from app.src.logging_config import logger, savedLevel
# from sqlalchemy import func, select
# from datetime import datetime, date, timedelta
# from dateutil.relativedelta import relativedelta
import logging
# import requests
# import os

bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    logger.debug(f"Home function entered in routes.py Session ID: {session.get('session_id')}")
    logger.info("Home page requested")

    # get README.md content
    # readme_file = get_file_content(os.getcwd() + '/README.md')

    logger.debug("Home function exited in routes.py")
    return render_template('home.html')#, content=readme_file)


security_questions = ["What is your hometown?", "What was the name of your first pet?", "What is your mother's maiden name?"]


# ------------------------------
@bp.route('/register', methods=['GET', 'POST'])
def register():
    logger.debug(f"Register function entered in routes.py method: {request.method}")
    logger.info("Registration attempt initiated")
    logger.debug(f"Session ID: {session.get('session_id')}")
    if request.method == 'POST':
        email = request.form['email']
        nickname = request.form['nickname']
        password = request.form['password']
        answer1 = request.form['answer1']
        answer2 = request.form['answer2']
        answer3 = request.form['answer3']
        # role = request.form.get('role') or 'user'

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
        user = User(email=email, nickname=nickname, password=hashed_password, security_answers=[answer1, answer2, answer3])#, role=role)
        db.session.add(user)
        db.session.commit()
        logger.debug(f"User {nickname} registered in database")
        logger.info(f"New user registered: {nickname}")

        flash("Registration successful! Please login.", "success")
        logger.debug("Register function exited with success in routes.py")
        return redirect(url_for('main.login'))
    
    logger.debug("Register function exited from GET request in routes.py")
    return render_template('register.html', security_questions=security_questions)


# ------------------------------
@bp.route('/login', methods=['GET', 'POST'])
def login():
    logger.debug(f"Login function entered in routes.py method: {request.method}")
    if request.method == 'POST':
        logger.info("Login attempt")
        logger.debug(f"Session ID: {session.get('session_id')}")
        identity = request.form['identity']
        password = request.form['password']

        # Search for user using nickname / email
        user = User.query.filter((User.email == identity) | (User.nickname == identity)).first()
        logger.debug(f"User found: {user.nickname if user else 'None'}")

        # Make sure the password matches
        if user and check_password_hash(user.password, password):
            login_user(user)
            logger.info(f"Authentication success for user: {user.nickname}")
            flash("Welcome back!", "success")
            logger.debug("Login function exited with success as user in routes.py")
            return redirect(url_for('main.dashboard'))

        else:
            logger.warning(f"Authentication failure for: {identity}")
            flash("Invalid credentials, try again.", "warning")
            logger.debug("Login function exited with authentication failure in routes.py")
            return redirect(url_for('main.login'))

    logger.debug("Login function exited from GET request in routes.py")
    return render_template('login.html')


#-------------------------------
@bp.route('/login/security', methods=['GET', 'POST'])
def login_security():
    logger.debug(f"Login security function entered in routes.py method: {request.method}")
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
            logger.debug("Login security function exited with success as user in routes.py")
            return redirect(url_for('main.profile'))
        else:
            logger.warning(f"Security question authentication failure for: {nickname} email: {email}")
            flash("Invalid credentials", "warning")
            logger.debug("Login security function exited with authentication failure in routes.py")
            return redirect(url_for('main.login_security'))

    logger.debug("Login security function exited from GET request in routes.py")
    return render_template('login_security.html', security_questions=security_questions)


# ------------------------------
@bp.route('/logout')
@login_required
def logout():
    logger.debug("Logout function entered in routes.py")
    logger.info(f"User logged out: {current_user.nickname}")
    logout_user()
    flash("You have been logged out.", "info")
    logger.debug("Logout function exited in routes.py")

    return redirect(url_for('main.login'))


#-------------------------------
@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    logger.debug(f"Profile function entered in routes.py with method: {request.method}")

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
        logger.debug("Profile function exited with success in routes.py")
        return redirect(url_for('main.profile'))
    
    # GET request handling
    userInfo = {'email': current_user.email, 'nickname': current_user.nickname}
    return render_template('profile.html', userInfo=userInfo)

#------------------------------
# Read files
def get_file_content(file_path):
    logger.debug(f"get_file_content function entered in routes.py for file: {file_path}")
    try:
        with open(file_path, 'r') as f:
            logger.debug(f"Successfully opened and read file: {file_path}")
            return f.read()
    except FileNotFoundError:
        logger.warning(f"File not found: {file_path}")
        return "File not found."
    except IOError as e:
        logger.warning(f"Error reading file: {e}")
        return "Error reading file."


logLevel = logging.DEBUG
# ------------------------------
# Used to change the log level at runtime from the logging info page
@bp.route('/logging-info', methods=['GET', 'POST'])
@login_required
def logging_info():
    logger.debug(f"logging_info function entered in routes.py method: {request.method}")
    # Get the handler and check if its found
    file_handler = current_app.config.get('FILE_HANDLER')

    if not file_handler:
        logger.warning("Set log level function exited (handler not found)")
        flash("Log handler not found!", "warning")
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        level = request.args.get('level').upper()

        levels = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING
            # 'ERROR': logging.ERROR
        }

        if level not in levels:
            logger.warning("Set log level function exited (not valid level)")
        else:
            file_handler.setLevel(levels[level])
            savedLevel("POST", level)
            flash(f"Log level changed to {level}", "info")
            logger.info(f"Log level changed to {level}")
            logger.debug("Set log level function exited with success")
        return redirect(url_for('main.dashboard'))