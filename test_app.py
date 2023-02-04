import pytest
import bcrypt
#from flask import Flask, session
#from flask_sqlalchemy import SQLAlchemy
from app import app, db, User, Reminder, Note
import regex as re

@pytest.fixture
def client():
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test_database.db"
    client = app.test_client()
    with app.app_context():
        db.create_all()

    yield client

    with app.app_context():
        db.drop_all()

def test_homepage(client):
    response = client.get('/')
    assert response.status_code == 200

def test_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200

def test_register_page(client):
    response = client.get('/register')
    assert response.status_code == 200

def test_register_user(client):
    with client.session_transaction() as session:
        response = client.post('/register', data={'username': 'testuser', 'password': 'Test12345', 'password_repeat': 'Test12345'})
        assert response.status_code == 302
        user = User.query.filter_by(username='testuser').first()
        assert user is not None
        assert bcrypt.checkpw('Test12345'.encode('utf-8'), user.password)

def test_register_user_error(client):
    with client.session_transaction() as session:
        response = client.post('/register', data={'username': 'testuser', 'password': 'test1234', 'password_repeat': 'test1234'})
        assert b"Password must contain an uppercase letter" in response.data
        user = User.query.filter_by(username='testuser').first()
        assert user is None

def test_login_user_error(client):
    with client.session_transaction() as session:
        response = client.post('/register', data={'username': 'testuser', 'password': 'Test12345', 'password_repeat': 'Test12345'})
        response = client.post('/login', data={'username': 'testuser', 'password': 'Test1234'})
        flash_msgs = response.data.decode('utf-8')
        assert re.search("Incorrect username or password", flash_msgs) is not None
        assert session.get('user_id') is None