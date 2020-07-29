from __future__ import absolute_import, unicode_literals
from .celery_utils import init_celery
from .sendemail import SendMail

from app.reports_sql import (
    OrionReportAccessPoint,
    UnpackData, OrionReportWalkwaysPerson
)

from datetime import datetime, timedelta
from calendar import monthrange

from app.xlsx_ import SaveReport

import os
import sqlite3


def dt_tw(wday):
    # Monday
    today = datetime.today()
    mon = today - timedelta(days = datetime.isoweekday(today)-1)
    if wday == 'm':
        return mon
    # Sunday
    if wday == 's':
        sun = mon + timedelta(days = 6)
        return sun
    # Today
    if wday == 't':
        return today



celery_app = init_celery()


# Connect to DB
def get_db():
    db = sqlite3.connect(
        os.path.join('./instance', 'app.sqlite'),
        detect_types=sqlite3.PARSE_DECLTYPES
    )
    db.row_factory = sqlite3.Row

    return db



@celery_app.task
def send_mail_task(id, report_id, recipient, periodicity, time, filename,
                            weekday=None, date=None):

    class MailTask:
        def __init__(self, id, report_id, recipient, periodicity, time,
                        textfile, weekday=None, date=None):
            self.id = id
            self.report_id = report_id
            self.recipient = recipient
            self.periodicity = periodicity
            self.weekday = weekday
            self.date = date
            self.time = time
            self.textfile = textfile


    mail_task = MailTask(id, report_id, recipient, periodicity, time,
                    filename, weekday, date)


    db = get_db()

    row = db.execute("SELECT id, report_type, name, period,\
                        data FROM saved_reports WHERE id = ?",
                         (mail_task.report_id,)).fetchone()
    if row:

        # Calculate time intervals
        if row['period'] == 'Previous week':
            date_start = (dt_tw('m') - timedelta(days = 7)).replace(hour=0, minute=0, second=0)
            date_end = (date_start + timedelta(days = 6)).replace(hour=23, minute=59, second=59)
        elif row['period'] == 'Previous day':
            date_start = dt_tw('t').replace(hour=0, minute=0, second=0)
            date_end = date_start.replace(hour=23, minute=59, second=59)
        elif row['period'] == 'Previous month':
            date_start = dt_tw('t').replace(day=1, hour=0, minute=0, second=0) - timedelta(month = 1)
            # Last day of current month
            last_day = monthrange(date_start.year, date_start.month)[1]
            date_end = date_start.replace(day=last_day, hour=23, minute=59, second=59)

        # For person
        if row['report_type'] == 'Person':
            persons_id = row['data']
            data = UnpackData(OrionReportWalkwaysPerson(date_start, date_end, persons_id))

        # For access point
        elif row['report_type'] == 'Access point':
            ap = eval(row['data'])['ap']
            events = eval(row['data'])['events']
            data = UnpackData(OrionReportAccessPoint(date_start, date_end, ap, events))

    xlsxfile = SaveReport(date_start, date_end, data, row['report_type'])
    subj = f"Automatic report system. Report: \"{row['name']}\", generated at {datetime.now().isoformat()}"

    mail_obj = SendMail(mail_task.textfile, xlsxfile, 'orion@localhost', mail_task.recipient, subj)
    mail_obj.start()
    return

@celery_app.task
def create_mail_task():
    from calendar import day_name

    db = get_db()
    cursor = db.execute("SELECT id, user_id, report_id, recipient,\
                         periodicity, time, weekday, date FROM mail_task;"
                        )
    row = cursor.fetchone()
    week_days = list(day_name)
    while row:
        now = datetime.now()
        countdown = now - now

        # To datetime format
        t = datetime.strptime(row['time'], '%H:%M:%S').time()

        if row['periodicity'] == 'daily':
            days = timedelta(days=0)
        if row['periodicity'] == 'weekly':
            # Count days
            days = (week_days.index(row['weekday']) - datetime.weekday(now) + 7) % 7
            days = timedelta(days=days)
        # elif mail_task.periodicity == 'monthly':
        #     pass

        # Count timedelta
        countdown = ((now + days).replace(hour=t.hour, minute=t.minute, second=t.second)
                            - now)


        # Do not create task if timedelta more than 86400 sec(24 hour)
        countdown = countdown.total_seconds()
        if countdown > 0 and countdown < 86400:

            username = 'Admin'
            if row['user_id'] != 10000000000:
                crsr = db.execute("SELECT username FROM user WHERE id=?",
                    (row['user_id'],)).fetchone()
                username = list(crsr).pop(0)
            filename = f"{os.path.join('./instance', 'textmsg')}/{username}_{row['id']}.txt"
            args = list(row)
            args.pop(1)
            args.insert(5, filename)
            send_mail_task.apply_async(args, countdown=countdown)

        row = cursor.fetchone()
    return
