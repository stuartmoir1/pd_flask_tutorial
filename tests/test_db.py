import sqlite3

import pytest
from flaskr.db import get_db

def test_get_close_db(app):
   # get_db returns the same connection each call
   with app.app_context():
      db = get_db()
      assert db is get_db()

   # db closes after context
   with pytest.raises(sqlite3.ProgrammingError) as e:
      db.execute('SELECT 1')
   assert 'closed' in str(e.value)

def test_init_db_command(runner, monkeypatch):
   class Recorder(object):
      called = False

   def fake_init_db():
      Recorder.called = True

   # fixture; replaces init_db with faked init_db function
   monkeypatch.setattr('flaskr.db.init_db', fake_init_db)
   
   # calls faked init_db and outputs message
   result = runner.invoke(args=['init-db'])
   assert 'Initialise' in result.output
   assert Recorder.called
