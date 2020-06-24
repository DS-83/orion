from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,
    session
)
from werkzeug.exceptions import abort

from app.auth import login_required
from app.db import get_db

bp = Blueprint('orion', __name__)

@bp.route('/')
@login_required
def index():
    return render_template('orion/index.html')


@bp.route('/mailing', methods=('GET', 'POST'))
@login_required
def mailing():

    db = get_db()
    reports = db.execute("SELECT id, name FROM saved_reports WHERE user_id = ?",
                        (session['user_id'],)
                        )
    if request.method == 'POST':
        reportname = request.form['reportname']
        recipient = request.form['recipient']
        period = request.form['periodicity']
        weekday = request.form.get('weekday')
        date = request.form.get('date')
        time = request.form['time']
    return render_template('orion/mailing.html', reports=reports)


# # Syncronising DB
# @bp.route('/syncdb', methods=('GET', 'POST'))
# @login_required
# def syncdb():
#     # This dic for render names and sync status of sync function
#     status = dict.fromkeys(SYNC_LIST, 0)
#     if request.method == 'POST':
#         error = None
#         # Take each method of Sync_obj class
#         for method in SYNC_LIST:
#             error = Sync_obj()
#             f = getattr(error, method)
#             f()
#             if error.success != True:
#                 return render_template('orion/syncdb.html', status=status)
#             # If successful sync
#             status[method] = 1
#         flash("DataBase sync was successful!")
#         return render_template('orion/syncdb.html', status=status)
#     return render_template('orion/syncdb.html', status=status)
