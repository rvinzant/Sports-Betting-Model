import pytest
from app import create_app, db

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-key'

@pytest.fixture
def app():
    app = create_app(TestConfig)
    yield app

@pytest.fixture
def client(app):
    # This provides the 'client' argument to your tests
    return app.test_client()

@pytest.fixture
def db_setup(app):
    with app.app_context():
        db.create_all()  # Create tables in the test DB
        yield db
        db.session.remove()
        db.drop_all()    # Clean up after the test

# run using: python -m pytest
# see which p/f: python -m pytest -v
# specific file: python -m pytest tests/test_auth.py