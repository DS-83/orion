from __future__ import absolute_import, unicode_literals

import os

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,
    session, current_app
)
from werkzeug.exceptions import abort

from app.auth import login_required, user_is_auth, user_first_logon
from app.db import get_db
from app.tasks import send_mail_task, dt_tw

from werkzeug.security import check_password_hash, generate_password_hash

from app.reports_sql import OrionQueryDashboard, UnpackData

from datetime import datetime
from time import strftime

import logging


from flask_babel import _

from app.serializer import verify_reset_token


# Logging config
logger = logging.getLogger(__name__)


bp = Blueprint('orion', __name__)


@bp.route('/')
@bp.route('/<page>')
@login_required
@user_first_logon
def index(page=None):

    #Calculate date and time
    date_end = (datetime.now()).replace(microsecond=0)

    if page is None :
        period = _('This week')
        date_start = (dt_tw('m')).replace(hour=0, minute=0, second=0, microsecond=0)
    elif page == 'day':
        period = _('This day')
        date_start = date_end.replace(hour=0, minute=0, second=0)
    else:
        period = _('This month')
        date_start = date_end.replace(day=1, hour=0, minute=0, second=0)


    # Data for Chart
    tick_step = 1
    labels = []
    data_l = []

    try:
        data = UnpackData(OrionQueryDashboard(date_start, date_end))

        # Check 'data' for data
        if len(data) > 1:
            # Chart labels
            labels = [l[0] for l in data[1:]]

            # Chart data
            data_l = [d[1] for d in data[1:]]

            # Tick display step
            max_val = max(data_l)
            if max_val > 18:
                tick_step = round(max_val / 12)

        #Label for chart
        str_date = _("Violations from: %(date_start)s to: %(date_end)s",
                        date_start=date_start, date_end=date_end)

    except:
        str_date = _("To display chart, administrator must configure connection to MSSQL server")


    return render_template('orion/index.html', labels=labels, data=data_l,
                            str_date=str_date, period=period, tick_step=tick_step
                            )


@bp.route('/mailing', methods=('GET', 'POST'))
@login_required
@user_first_logon
def mailing():

    db = get_db()

    reports = db.execute("SELECT id, name FROM saved_reports WHERE user_id = ?",
                        (session['user_id'],)
                        )
    # Get Admin id
    admin_id = db.execute("SELECT id FROM admin;").fetchone()
    # Mail tasks
    # Administrator must see all mail tasks
    if session['user_id'] == admin_id['id']:
        cursor = db.execute("SELECT mail_task.id, user.username,\
                                    saved_reports.name, recipient,\
                                    periodicity, weekday, date, time\
                            FROM mail_task\
                            LEFT JOIN saved_reports\
                            ON mail_task.report_id = saved_reports.id\
                            LEFT JOIN user\
                            ON mail_task.user_id = user.id;")
    else:
        cursor = db.execute("SELECT mail_task.id, saved_reports.name,\
                                    recipient, periodicity,\
                                    weekday, date, time\
                            FROM mail_task\
                            LEFT JOIN saved_reports\
                            ON mail_task.report_id = saved_reports.id\
                            WHERE mail_task.user_id = ?;",
                            (session['user_id'],)
                          )
    row = cursor.fetchone()
    tasks = []
    if row:
        tasks.append(row.keys())
        while row:
            tasks.append(row)
            row = cursor.fetchone()



    if request.method == 'POST':
        error = None
        date = None
        weekday = None
        report_id = request.form['reportname']
        if not report_id:
            error = _('Must choose report.')
        recipient = request.form['recipient']
        if not recipient:
            error = _('Recipient can not be blank.')
        periodicity = request.form['periodicity']
        if periodicity == 'monthly':
            date = request.form.get('date')
            if not date or int(date) > 29 or int(date) < 1:
                error = _('Date must be in between 1 and 29 include.')
        elif periodicity == 'weekly':
            weekday = request.form.get('weekday')
        time = request.form['time']
        # Create text file with text message`
        textmsg = request.form['text_message']
        if not textmsg:
            error = _('Message text can not be blank.')

        if error is None:
            try:
                cursor = db.execute("INSERT INTO mail_task\
                           (user_id, report_id, recipient, periodicity,\
                           weekday, date, time) VALUES (?,?,?,?,?,?,?);",
                           (session['user_id'], report_id, recipient,
                           periodicity, weekday, date, time)
                           )
                task_id = cursor.lastrowid

                filename = f"{current_app.config['TEXTFILE_FOLDER']}/{str(g.user['username'])}_{task_id}.txt"
                with open(filename, 'w') as f:
                    f.write(textmsg)

                # Create mail task
                celery_id = create_mail_task(task_id)

                db.commit()

                # Write celery task id to DB
                if celery_id:
                    cursor = db.execute("UPDATE mail_task\
                               SET celery_id = ? WHERE id = ?;",
                               (celery_id, task_id)
                               )
                    db.commit()

                flash(_('Success'), 'success')
                return redirect(url_for('orion.mailing'))
            except Exception as error:
                flash(error, 'warning')
        else:
            flash(error, 'warning')

    # Check if smtp configured
    server_mail = db.execute("SELECT * FROM smtp;").fetchone()

    return render_template('orion/mailing.html', reports=reports,
                            tasks=tasks, server_mail=server_mail)

# Delete task
@bp.route('/mailing/delete', methods=['POST'])
@login_required
@user_first_logon
def delete():

    from .celery_utils import celery_app

    db = get_db()

    # Get Admin id
    admin_id = db.execute("SELECT id FROM admin;").fetchone()

    id = request.form['hidden_id_del']

    try:
        # For Admin
        if session['user_id'] == admin_id['id']:
            row = db.execute("SELECT celery_id\
                              FROM mail_task\
                              WHERE id = ?", (id,)
                              ).fetchone()
        # For other users
        else:
            row = db.execute("SELECT celery_id\
                              FROM mail_task\
                              WHERE id = ? AND user_id = ?", (id, session['user_id'])
                              ).fetchone()

        #  Revoke celery task
        if row['celery_id']:
            celery_app.control.revoke(row['celery_id'])
            celery_app.control.terminate(row['celery_id'])

        # Delete task from DB for Admin
        if session['user_id'] == admin_id:
            db.execute("DELETE FROM mail_task\
                        WHERE id = ?", (id,))
        # Delete task from DB for other users
        else:
            db.execute("DELETE FROM mail_task\
                        WHERE id = ? AND user_id = ?", (id, session['user_id']))
        db.commit()

        flash(_('Successfuly delete'), 'success')
    except Exception as err:
        flash(err, 'warning')

    return redirect(url_for('orion.mailing'))

# Create celery task if task is today task
def create_mail_task(id):
    from datetime import datetime, timedelta
    from calendar import day_name

    celery_id = None

    db = get_db()
    cursor = db.execute("SELECT id, report_id, recipient, periodicity, time,\
                        weekday, date FROM mail_task WHERE id = ?;",
                        (id,)
                        )
    row = cursor.fetchone()
    week_days = list(day_name)
    if row:
        now = datetime.now()
        countdown = 0
        filename = f"{current_app.config['TEXTFILE_FOLDER']}/{str(g.user['username'])}_{id}.txt"

        # To datetime format
        t = datetime.strptime(row['time'], '%H:%M:%S').time()

        if row['periodicity'] == 'daily':
            countdown = (now.replace(hour=t.hour, minute=t.minute, second=t.second)
                                - now)
        elif row['periodicity'] == 'weekly':
            # Count days
            days = (week_days.index(row['weekday']) - datetime.weekday(now) + 7) % 7
            days = timedelta(days=days)
            # Count timedelta
            countdown = ((now + days).replace(hour=t.hour, minute=t.minute, second=t.second)
                            - now)
        elif row['periodicity'] == 'monthly':
            countdown = (now.replace(day = row['date'],
                    hour=t.hour, minute=t.minute, second=t.second) - now)

        countdown = countdown.total_seconds()
        if countdown > 0 and countdown < 86400 - now.hour * 3600 - now.minute * 60 - now.second:
            args = list(row)
            args.insert(5, filename)
            celery_id = send_mail_task.apply_async(args, countdown=countdown).id

    return celery_id


@bp.route('/changepass', methods=('GET', 'POST'))
@login_required
def changepass():
    if request.method == 'POST':
        db = get_db()
        error = None

        current_pass = request.form['CurrentPassword']

        if not check_password_hash(g.user['password'], current_pass):
            error = _('Incorrect current password.')

        # Check new password and re-enter password
        if error is None:
            new_pass = request.form['NewPassword']
            re_new_pass = request.form['ReNewPassword']
            if new_pass != re_new_pass:
                error = _('Password mismatch')
            else:
                if g.user['username'] == 'Admin':
                    table_name = 'admin'
                else:
                    table_name = 'user'

                new_pass = generate_password_hash(new_pass)

                try:
                    db.execute(f"UPDATE {table_name}\
                                 SET password = ?, first_logon = 0\
                                 WHERE id = ?",
                                (new_pass, g.user['id']))
                    db.commit()

                    session.clear()
                    flash(_('Password successfuly changed'), 'success')
                    return redirect(url_for('auth.login'))
                except Exception as error:
                    flash(error, 'warning')

        flash(error, 'warning')

    return render_template('orion/changepass.html')


# Reset password route
@bp.route('/reset_password/<token>', methods=('GET', 'POST'))
@user_is_auth
def reset_password(token):

    error = None

    user_id = verify_reset_token(token)
    if user_id is None:
        error = _('Invalid or expired link. Contact your system administrator')
        flash(error, 'warning')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        db = get_db()

        # Check new password and re-enter password
        new_pass = request.form['NewPassword']
        re_new_pass = request.form['ReNewPassword']
        if new_pass != re_new_pass:
            error = _('Password mismatch')
        else:
            new_pass = generate_password_hash(new_pass)

            try:
                db.execute(f"UPDATE user SET password = ? WHERE id = ?",
                            (new_pass, user_id))
                db.commit()

                session.clear()
                flash(_('Password successfuly changed'), 'success')
                logger.info(f"Password successfuly changed for user id: {user_id}")
                return redirect(url_for('auth.login'))
            except Exception as error:
                flash(error, 'warning')
                logger.warning(error)

        flash(error, 'warning')

    return render_template('orion/resetpass.html')
