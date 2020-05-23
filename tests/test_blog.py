import pytest
from flaskr.db import get_db

def test_index(client, auth):
   response = client.get('/')

   # not logged in - links available
   assert b'Log In' in response.data
   assert b'Register' in response.data

   # not logged in - link not available
   assert b'href="/1/update"' not in response.data
   assert b'href="/1/view"' not in response.data

   # logged in...
   auth.login()
   response = client.get('/')

   # ...log out link available
   assert b'Log Out' in response.data

   # ... update link available
   assert b'href="/1/update"' in response.data
   assert b'href="/1/view"' not in response.data

   # ...user data available
   assert b'test title' in response.data
   assert b'by test on 2018-01-01' in response.data
   assert b'test\nbody' in response.data

   # logged out...
   auth.logout()
   response = client.get('/')

   # update and view links not available
   assert b'href="/1/update"' not in response.data
   assert b'href="/1/view"' not in response.data   
   
   # logged in as different user...
   auth.login('other', 'other')
   response = client.get('/')

   # ...view link available
   assert b'href="/1/update"' not in response.data
   assert b'href="/1/view"' in response.data

@pytest.mark.parametrize( 'path', ('/create', '/1/update', '/1/delete'))
def test_login_required(client, path):
   # not logged in - routes to login
   response = client.post(path)
   assert response.headers['Location'] == 'http://localhost/auth/login'

def test_author_required(app, client, auth):
   # change the post author to another author
   with app.app_context():
      db = get_db()
      db.execute('UPDATE post SET author_id = 2 WHERE id = 1')
      db.commit()

   auth.login()
   # current user cannot modify other user post
   assert client.post('/1/update').status_code == 403
   assert client.post('/1/delete').status_code == 403
   # current user does not see edit link
   assert b"href='/1/update'" not in client.get('/').data

@pytest.mark.parametrize('path', ('/2/update', '/2/delete'))
def test_exists_required(client, auth, path):
   auth.login()
   # cannot update or delete where post does not exist
   assert client.post(path).status_code == 404

def test_create(client, auth, app):
   auth.login()
   # view renders
   assert client.get('/create').status_code == 200
   client.post('/create', data={ 'title': 'create', 'body': '' })

   with app.app_context():
      db = get_db()
      # post created
      assert db.execute('SELECT COUNT(id) FROM post').fetchone()[0] == 2

def test_view(client, auth, app):
   # view not logged in
   assert client.get('/1/view').status_code == 200

   # view logged in
   auth.login()
   assert client.get('/1/view').status_code == 200

def test_update(client, auth, app):
   auth.login()
   # view renders
   assert client.get('/1/update').status_code == 200
   client.post('/1/update', data={ "title": 'updated', 'body': '' })

   with app.app_context():
      db = get_db()
      post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
      # post updated
      assert post['title'] == 'updated'

@pytest.mark.parametrize('path', ('/create', '/1/update'))
def test_create_update_validate(client, auth, path):
   auth.login()
   response = client.post(path, data={ "title": '', 'body': '' })
   # title required
   assert b'Title is required.' in response.data

def test_delete(client, auth, app):
   auth.login()
   response = client.post('/1/delete')
   # routes to root view after delete
   assert response.headers['Location'] == 'http://localhost/'

   with app.app_context():
      db = get_db()
      post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
      # post deleted
      assert post is None
   