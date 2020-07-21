from __future__ import absolute_import, unicode_literals
from .celery_utils import init_celery
from .sendemail import SendMail

from app.reports_sql import (
    OrionReportAccessPoint,
    UnpackData, OrionReportWalkwaysPerson
)

from datetime import datetime, timedelta

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




# @celery.task
# def add_together(a, b):
#     return a + b
celery_app = init_celery()

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


    def get_db():
        db = sqlite3.connect(
            os.path.join('./instance', 'app.sqlite'),
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        db.row_factory = sqlite3.Row

        return db


    db = get_db()

    print(report_id)
    # print(type(mail_task))
    # print(mail_task[0])

    row = db.execute("SELECT id, report, name, period,\
                        data FROM saved_reports WHERE id = ?",
                         (mail_task.report_id,)).fetchone()
    if row:
        # For person
        if row['report'] == 'Person':
            print(row['data'])
            persons_id = row['data']
            print(type(persons_id))
            if row['period'] == 'Previous week':
                date_start = (dt_tw('m') - timedelta(days = 7)).replace(hour=0, minute=0, second=0)
                date_end = (date_start + timedelta(days = 6)).replace(hour=23, minute=59, second=59)

            data = UnpackData(OrionReportWalkwaysPerson(date_start, date_end, persons_id))
            xlsxfile = SaveReport(date_start, date_end, data, row['report'])
            subj = f"Automatic report system. Report {row['report']}, generated at {datetime.now().isoformat()}"
    #     # For access point
    # elif row['report'] == 'Access point':
    #         d = eval(row['data'])
    #         aps_id = d['ap'].split(',')
    #         data_orion = UnpackData(OrionQueryAccessPoints())
    #         report_data = []
    #         l = []
    #         for r in data_orion:
    #             for ap in aps_id:
    #                 if int(ap) == r[1]:
    #                     l.append(r[0])
    #         report_data.append(l)
    #         events_id = d['events'].split(',')
    #         data_orion = UnpackData(OrionQueryEvents())
    #         l = []
    #         for r in data_orion:
    #             for event in events_id:
    #                 if int(event) == r[0]:
    #                     l.append(r[1])
    #         report_data.append(l)


    mail_obj = SendMail(mail_task.textfile, xlsxfile, 'orion@localhost', mail_task.recipient, subj)
    mail_obj.start()
    return

def create_mail_task():
    from datetime import datetime, timedelta
    from calendar import day_name
    from json import dumps


    class MailTask:
        def __init__(self, id, report_id, recipient, periodicity, time, weekday=None, date=None):
            self.id = id
            self.report_id = report_id
            self.recipient = recipient
            self.periodicity = periodicity
            self.weekday = weekday
            self.date = date
            self.time = time

        def toJSON(self):
            return dumps(self, default=lambda o: o.__dict__,
                sort_keys=True, indent=4)

    db = get_db()
    cursor = db.execute("SELECT id, report_id, recipient, periodicity, time,\
                        weekday, date FROM mail_task;"
                        )
    row = cursor.fetchone()
    week_days = list(day_name)
    while row:
        now = datetime.now()
        countdown = 0
        mail_task = MailTask(row['id'], row['report_id'], row['recipient'],
                        row['periodicity'], row['time'], row['weekday'],
                        row['date'])
        # if mail_task.periodicity == 'daily':
        #     pass
        if mail_task.periodicity == 'weekly':
            # To datetime format
            t = datetime.strptime(mail_task.time, '%H:%M:%S').time()
            # Count days
            days = (week_days.index(mail_task.weekday) - datetime.weekday(now) + 7) % 7
            days = timedelta(days=days)
            # Count timedelta
            countdown = ((now + days).replace(hour=t.hour, minute=t.minute, second=t.second)
                            - now)
            # Do not create task if timedelta more than 86400 sec(24 hour)
        # elif mail_task.periodicity == 'monthly':
        #     pass
            if countdown > 86400:
                continue
            args = [mail_task.toJSON()]
            send_mail_task.apply_async(args, countdown=countdown.total_seconds())

        row = cursor.fetchone()
    return
