from flaskr import create_app

def test_config():
  # not in test mode unless config testing
  assert not create_app().testing
  assert create_app({ 'TESTING': True }).testing

def test_hello(client):
  # route return expected data
  response = client.get('/hello')
  assert response.data == b'Hello, World!'