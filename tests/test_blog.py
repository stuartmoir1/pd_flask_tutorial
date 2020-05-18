import pytest
from flaskr import get_db

def test_index(client, auth):
  response = client.get('/')
  assert b'Log In' in response.data
  assert b'Register' in response.data

  auth.login()
  response = client.get('/')
  assert b'Log Out' in response_data
  assert b'test title' in response_data
  assert b'by test on 2018-01-01' in response_data
  assert b'test\nbody' in response_data
  assert b'href=\'/1/update/\'' in response_data