from flask import (
   Blueprint,
   flash,
   g,
   redirect,
   render_template,
   request,
   url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
   db = get_db()
   posts = db.execute(
      'SELECT p.id, title, body, created, username,'
      ' p.author_id as author_id,'
      ' COUNT(v.post_id) as count'
      ' FROM post p'
      ' JOIN user u ON p.author_id = u.id'
      ' LEFT JOIN vote v ON p.id = v.post_id'
      ' GROUP BY p.id'
      ' ORDER BY created DESC'
   ).fetchall()

   return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
   if request.method == 'POST':
      title = request.form['title']
      body = request.form['body']
      error = None
      
      if not title:
         error = 'Title is required.'

      if error is not None:
         flash(error)
      else:
         db = get_db()
         db.execute(
            'INSERT INTO post (title, body, author_id)'
            ' VALUES (?, ?, ?)',
            (title, body, g.user['id'])
         )
         db.commit()
         return redirect(url_for('blog.index'))

   return render_template('blog/create.html')

def get_post(id, check_author=True):
   post = get_db().execute(
      'SELECT p.id, title, body, created, author_id, username'
      ' FROM post p JOIN user u ON p.author_id = u.id'
      ' WHERE p.id = ?',
      (id,) # comma reqd for single arg
   ).fetchone()

   if post is None:
      # 404 not found
      abort(404, 'Post id {0} doesn\'t exist'.format(id))
   if check_author and post['author_id'] != g.user['id']:
      # 403 forbidden
      abort(403)

   return post

def get_vote(post_id):
   vote = get_db().execute(
      'SELECT * FROM vote WHERE post_id = ? AND author_id = ?',
      (post_id, g.user['id'])
   ).fetchone()

   return vote

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
   post = get_post(id)
   vote = True if get_vote(id) else False

   print('VOTE')
   print(vote)
   
   if request.method == 'POST':
      title = request.form['title']
      body = request.form['body']
      like = True if 'like' in request.form else False
      error = None

      if not title:
         error = 'Title is required.'

      if error is not None:
         flash(error)
      else:
         db = get_db()
         db.execute(
            'UPDATE post SET title = ?, body = ?'
            ' WHERE id = ?',
            (title, body, id)
         )

         if like:
            # create vote if it does not exist
            if not vote:
               db.execute(
                  'INSERT INTO vote (post_id, author_id)'
                  ' VALUES (?, ?) ',
                  (id, g.user['id'])
               )
         else:
            # delete vote if it exists
            if vote:
               db.execute(
                  'DELETE FROM vote WHERE post_id = ? AND author_id = ?',
                  (id, g.user['id'])
               )

         db.commit()
         return redirect(url_for('blog.index'))

   return render_template('blog/update.html', post=post, vote=vote)

@bp.route('/<int:id>/delete', methods=('POST', ))
@login_required
def delete(id):
   get_post(id)
   db = get_db()
   db.execute(
      'DELETE FROM post WHERE id = ?',
      (id,) # comma reqd for single arg
   )
   db.commit()
   return redirect(url_for('blog.index'))

@bp.route('/<int:id>/view', methods=('GET', 'POST'))
def view(id):
   post = get_post(id, False)
   vote = True if get_vote(id) else False

   if request.method == 'POST':
      like = True if 'like' in request.form else False
      db = get_db()

      if like:
         # create vote if it does not exist
         if not vote:
            db.execute(
               'INSERT INTO vote (post_id, author_id)'
               ' VALUES (?, ?) ',
               (id, g.user['id'])
            )
      else:
         # delete vote if it exists
         if vote:
            db.execute(
               'DELETE FROM vote WHERE post_id = ? AND author_id = ?',
               (id, g.user['id'])
            )

      db.commit()
      return redirect(url_for('blog.index'))

   return render_template('blog/view.html', post=post, vote=vote)
