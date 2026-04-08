from app.models import User
from werkzeug.security import generate_password_hash
from flask_login import current_user

def test_register_success(client, db_setup):
    # Simulate filling out the registration form
    response = client.post('/register', data={
        'email': 'new@test.com',
        'nickname': 'newuser',
        'password': 'password123',
        'answer1': 'Hometown',
        'answer2': 'PetName',
        'answer3': 'MaidenName'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert response.request.path == '/login'
    # # if follow redirects is false, check where trying to go
    # assert response.headers['Location'] == '/login'
    # Check if user actually exists in DB
    assert User.query.filter_by(email='new@test.com').first() is not None

def test_register_duplicate_email(client, db_setup):
    # First, create a user manually in the test DB
    user = User(email='taken@test.com', nickname='original', password='hash', security_answers=['a','b','c'])
    db_setup.session.add(user)
    db_setup.session.commit()

    # Try to register with the same email
    response = client.post('/register', data={
        'email': 'taken@test.com',
        'nickname': 'different',
        'password': 'password123',
        'answer1': 'a', 'answer2': 'b', 'answer3': 'c'
    }, follow_redirects=True)

    assert response.request.path == '/register'

def test_login_success(client, db_setup):
    # 1. Setup: Create a user with a hashed password
    user = User(email='login@test.com', nickname='tester', 
                password=generate_password_hash('correct_pass'),
                security_answers=['a','b','c'])
    db_setup.session.add(user)
    db_setup.session.commit()

    # 2. Act: Try logging in with the email
    response = client.post('/login', data={
        'identity': 'login@test.com',
        'password': 'correct_pass'
    }, follow_redirects=True)

    # 3. Assert
    assert b"Welcome back" in response.data
    assert current_user.is_authenticated
    assert response.request.path == '/dashboard' # Check redirect

def test_login_invalid_password(client, db_setup):
    response = client.post('/login', data={
        'identity': 'nonexistent@test.com',
        'password': 'wrong'
    }, follow_redirects=True)
    
    assert b"Invalid credentials" in response.data
    assert response.request.path == '/login'

def test_login_security_success(client, db_setup):
    user = User(email='sec@test.com', nickname='sec_user', 
                password='hash', security_answers=['Hometown', 'Pet', 'Maiden'])
    db_setup.session.add(user)
    db_setup.session.commit()

    # Test answering the first question correctly
    response = client.post('/login/security', data={
        'email': 'sec@test.com',
        'nickname': 'sec_user',
        'security_question': "What is your hometown?",
        'security_answer': 'hometown' # Testing case-insensitivity
    }, follow_redirects=True)

    assert b"Welcome back" in response.data
    assert response.request.path == '/profile'

def test_logout(client, db_setup):
    # First, log the user in using the session helper
    user = User(email='out@test.com', nickname='logout_me', password='hash', security_answers=['a','b','c'])
    db_setup.session.add(user)
    db_setup.session.commit()

    with client:
        client.post('/login', data={'identity': 'out@test.com', 'password': 'hash'})
        
        # Now trigger logout
        response = client.get('/logout', follow_redirects=True)
        assert response.request.path == '/login'
        
        # Verify user is no longer in current_user
        assert current_user.is_authenticated is False


