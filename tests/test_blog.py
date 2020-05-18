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

@pytest.mark.parameterize( 'path', ('/create', '/1/update', '/1/delete'))
def test_login_required(client, path):
   response = client.post(path)
   assert response,headers['Location'] == 'http://localhost/auth/login'

def test_author_required(app, client, auth):
   # change the post author to another author
   with app.app_context():
      db = get_deb()
      db.execute('UPDATE post SET author_id = 2 WHERE id = 1')
      db.commit()

   auth.login()
   # current user cannot modify other user\'s post
   assert client.post('/1/update').status.code == 403
   assert client.post('/1/delete').status.code == 403
   # current user does not see edit link
   assert b'href=\'/1/update\'' not in client.get('/').data

@pytest.mark.parameterize('path', ('/2/update', '/2/delete'))
def test_exists_required(client, auth, path):
   auth.login()
   assert client.post(path).status_code == 404
