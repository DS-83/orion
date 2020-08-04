from __future__ import absolute_import, unicode_literals

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,
    session, current_app
)
from werkzeug.exceptions import abort

from app.auth import login_required
from app.db import get_db
from app.tasks import send_mail_task


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
    #Mail tasks
    cursor = db.execute("SELECT saved_reports.name, recipient, periodicity,\
                               weekday, date, time, mail_task.id FROM mail_task\
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
            error = 'Must choose report.'
        recipient = request.form['recipient']
        if not recipient:
            error = 'Recipient can not be blank.'
        periodicity = request.form['periodicity']
        if periodicity == 'monthly':
            date = request.form.get('date')
            if not date or int(date) > 29 or int(date) < 1:
                error = 'Date must be in between 1 and 29 include.'
        elif periodicity == 'weekly':
            weekday = request.form.get('weekday')
        time = request.form['time']
        # Create text file with text message`
        textmsg = request.form['text_message']
        if not textmsg:
            error = 'Message text can not be blank.'

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

                flash('Success', 'success')
                return redirect(url_for('orion.mailing'))
            except Exception as error:
                flash(error, 'warning')
        else:
            flash(error, 'warning')

    return render_template('orion/mailing.html', reports=reports, tasks=tasks)

# Delete task
@bp.route('/mailing/delete', methods=['POST'])
@login_required
def delete():

    from .celery_utils import celery_app

    db = get_db()
    id = request.form['hidden_id']
    try:
        row = db.execute("SELECT celery_id\
                          FROM mail_task\
                          WHERE id = ?", (id,)
                          ).fetchone()

        # # Revoke celery task
        if row['celery_id']:
            celery_app.control.revoke(row['celery_id'])
            celery_app.control.terminate(row['celery_id'])

        # Delete task from DB
        db.execute("DELETE FROM mail_task WHERE id = ?", (id,))
        db.commit()

        flash('Success', 'success')
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
