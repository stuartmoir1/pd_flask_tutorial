import pytest
from flask import g, session
from flaskr.db import get_db

def test_register(client, app):
   # view renders
   assert client.get('/auth/register').status_code == 200

   response = client.post(
      '/auth/register',
      data={ 'username': 'a', 'password': 'a' }
   )
   # routes to login view after register
   assert response.headers['Location'] == 'http://localhost/auth/login'

   # user registered
   with app.app_context():
      assert get_db().execute(
        "SELECT * FROM user WHERE username='a'"
      ).fetchone() is not None

@pytest.mark.parametrize(
   ('username', 'password', 'message'),
   (
      ('', '', b'Username is required.'),
      ('a', '', b'Password is required.'),
      ('test', 'test', b'already registered')
   ))
def test_register_validate_input(client, username, password, message):
   response = client.post(
      'auth/register',
      data={ 'username': username, 'password': password }
   )
   # registration errors
   assert message in response.data

def test_login(client, auth):
   # view renders
   assert client.get('/auth/login').status_code == 200

   response = auth.login()
   # routes to root view after login
   assert response.headers['Location'] == 'http://localhost/'

   with client:
      client.get('/')
      # user in browser data
      assert session['user_id'] == 1
      assert g.user['username'] == 'test'

@pytest.mark.parametrize(
   ('username', 'password', 'message'),
   (
      ('a', 'test', b'Incorrect username.'),
      ('test', 'a', b'Incorrect password.')
   ))
def test_login_validate_input(auth, username, password, message):
   response = auth.login(username, password)
   # login errors
   assert message in response.data

def test_logout(client, auth):
   auth.login()
   with client:
      auth.logout()
      # user not in browser data
      assert 'user_id' not in session
