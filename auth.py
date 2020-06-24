import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from app.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


# Login route
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        # Make username case insesitive
        username = request.form['username'][0].upper() + request.form['username'][1:].lower()
        password = request.form['password']
        db = get_db()
        error = None
        # verification for built-in administrator account
        if username == 'Admin':
            user = db.execute(
                "SELECT * FROM admin WHERE username = 'Admin';"
            ).fetchone()
        else:
            user = db.execute(
                'SELECT * FROM user WHERE username = ?', (username,)
            ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
        # Check for disabled account
        elif user['status'] == 'disabled':
            error = "Account disabled"

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('orion.index'))

        flash(error, 'error')

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    elif user_id == 10000000000:
        g.user = get_db().execute(
            'SELECT * FROM admin WHERE id = ?', (user_id,)
        ).fetchone()
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

# Logout route
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


# Require Authentication in Other Views
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

# User role-based view
def user_role(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not g.user['IsAdmin']:
            session.clear()
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
