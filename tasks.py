from .celery_utils import celery_app
from .sendemail import SendMail

from app.reports_sql import (
    OrionReportAccessPoint,
    UnpackData, OrionReportWalkwaysPerson, OrionReportViolations
)

from datetime import datetime, timedelta
from calendar import monthrange
from dateutil.relativedelta import relativedelta

from app.xlsx_ import SaveReport

from app.db import get_db_no_g

import os


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



@celery_app.task
def send_mail_task(id, report_id, recipient, periodicity, time, filename,
                            weekday=None, date=None):


    db = get_db_no_g()

    row = db.execute("SELECT id, report_type, name, period,\
                        data FROM saved_reports WHERE id = ?",
                         (report_id,)).fetchone()
    if row:

        # Calculate time intervals
        if row['period'] == 'Previous week':
            date_start = (dt_tw('m') - timedelta(days = 7)).replace(hour=0, minute=0, second=0)
            date_end = (date_start + timedelta(days = 6)).replace(hour=23, minute=59, second=59)

        elif row['period'] == 'Previous day':
            date_start = dt_tw('t').replace(hour=0, minute=0, second=0) - timedelta(days=1)
            date_end = date_start.replace(hour=23, minute=59, second=59)

        elif row['period'] == 'Previous month':
            date_start = dt_tw('t').replace(day=1, hour=0, minute=0, second=0) - relativedelta(months = 1)
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

        # For violations
        elif row['report_type'] == 'Violations':
            ap = row['data']
            data = UnpackData(OrionReportViolations(date_start, date_end), ap)

    xlsxfile = SaveReport(date_start, date_end, data, row['name'])
    subj = f"Automatic report system. Report: \"{row['name']}\", generated at {datetime.now().isoformat()}"

    mail_obj = SendMail(filename, xlsxfile, 'orion@localhost', recipient, subj)
    mail_obj.start()
    return

@celery_app.task
def create_mail_task():
    from calendar import day_name

    celery_id = None

    db = get_db_no_g()
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
        elif row['periodicity'] == 'weekly':
            # Count days
            days = (week_days.index(row['weekday']) - datetime.weekday(now) + 7) % 7
            days = timedelta(days=days)
        elif row['periodicity'] == 'monthly':
            if row['date'] == now.day:
                days = timedelta(days=0)
            else:
                days = timedelta(days=-1)

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
            celery_id = send_mail_task.apply_async(args, countdown=countdown).id

            # Write celery task id to DB
            if celery_id:
                db.execute("UPDATE mail_task\
                           SET celery_id = ? WHERE id = ?;",
                           (celery_id, row['id'])
                           )
                db.commit()

        row = cursor.fetchone()
    return
