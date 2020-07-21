# from zeep import helpers, xsd
# from settings import client
# from db import get_mssql
#
# # Person attr
# PERSON_ATTR = ['AccessLevelId', 'Department', 'EmailList', 'Itn',\
#  'Address', 'DepartmentId', 'ExternalId', 'LastName', 'ArchivingTimeStamp',\
#  'DismissedComment', 'FirstName', 'MiddleName', 'BirthDate',\
#  'DocumentEndingDate', 'HomePhone', 'Phone', 'Birthplace',\
#  'DocumentIsser', 'Id', 'Photo', 'BlackListComment', 'DocumentIsserCode',\
#  'IsDismissed', 'Position', 'ChangeTime', 'DocumentIssueDate',\
#  'IsFreeShedule', 'PositionId', 'Company', 'DocumentNumber',\
#  'IsInArchive', 'Sex', 'CompanyId', 'DocumentSerials', 'IsInBlackList',\
#  'Status', 'ContactIdIndex', 'DocumentType', 'IsLockedDayCrossing', 'TabNum']
#
#
# # Get Person by id and replase None values to SkipValues
# def IntGetPersonById(id):
#     person = client.service.GetPersonById(id, 1, 0)
#     # Replace None to SkipValue
#     for attrib in PERSON_ATTR:
#         if getattr(person.OperationResult, attrib) == None:
#             setattr(person.OperationResult, attrib, xsd.SkipValue)
#     return person
#
# # Get Persons by any field
# def IntGetPersonByAny(filter):
#     person = []
#     for key in filter.keys():
#         for atr in PERSON_ATTR:
#             if key == atr:
#                     person.append(f"{key}={filter[key]}")
#             person.append(xsd.SkipValue)
#     print(person)
#     return client.service.GetPersons(1, 0, 0, person, 0, 0, 0)
#
# # Get person pass list
# def IntGetPersonPassList(person):
#     with client.settings(raw_response=True):
#         rw_response = client.service.GetPersonPassList(person.OperationResult, 0)
#     otag = "<item>"
#     ctag = "</item>"
#     return ParsStringTag(rw_response.text, otag, ctag)
#
# # Parsing raw xml string
# def ParsStringTag(string, otag, ctag):
#     result = []
#     # Index of open tag in string
#     indxf = string.find(otag)
#     # Repeat until end
#     while indxf != -1:
#         # Index of closing tag in string
#         indxn = string.find(ctag, indxf)
#         # Get value and append to result
#         result.append(string[indxf + len(otag): indxn])
#         indxf = string.find(otag, indxn + len(ctag))
#     return result
#
#
# # # Get entry points list
# def IntGetEntryPointsList():
#     # Raw response
#     with client.settings(raw_response=True):
#         rw_response = client.service.GetEntryPoints(0,0,0)
#     # Parse once
#     rlist = ParsStringTag(rw_response.text, "<Readers ", "</Readers>")
#     # Parse one more time
#     rlist1 = []
#     for i in rlist:
#         rlist1.append(ParsStringTag(i, "<item>", "</item>"))
#     # Get binary responce
#     b_responce = client.service.GetEntryPoints(0,0,0)
#     # Convert to dict
#     ser = helpers.serialize_object(b_responce.OperationResult)
#     # Add Readers to Dict
#     k = len(rlist1) - 1
#     m = len(ser) - 1
#     while k >= 0:
#         if ser[m].get('Readers'):
#             ser[m].update({'Readers': rlist1[k]})
#             k -= 1
#             m -= 1
#         else:
#             m -= 1
#     # Check consistency
#     if k != m or m != -1:
#         error = "Error in IntGetEntryPointsList func."
#         return error
#     return ser
import pyodbc
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






from datetime import datetime
#
# def get_mssql():
#     server = '192.168.0.55'
#     database = 'Orionnew'
#     username = 'sa'
#     password = '123456'
#
#     conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};\
#                            SERVER='+server+';DATABASE='+database+';\
#                            UID='+username+';PWD='+ password
#                            )
#     cursor = conn.cursor()
#     return cursor

# Unpack Data
def UnpackData(data):
    result = []
    columns = [column[0] for column in data.description]
    result.append(columns)
    row = data.fetchone()
    while row:
        result.append(row)
        row = data.fetchone()
    data.close()
    return result


def OrionQueryEvents():
    db = get_mssql()
    db.execute("SELECT Event, Contents\
                FROM Events\
                WHERE Event IN (25,26,27,28,29,30,31,32,33,219,34)\
                ORDER BY Event;"
                )
    return db

def OrionQueryAccessPoints():
    db = get_mssql()
    db.execute("SELECT Name, GIndex AS DoorIndex, ID\
                FROM AcessPoint\
                ORDER BY GIndex;"
                )
    return db

def OrionReportAccessPoint():
    db = get_mssql()
    date_start = datetime(2018, 10, 27, 22, 1, 19)
    date_end = datetime(2018, 10, 27, 22, 29, 19)
    db.execute("SELECT pLogData.TimeVal, pLogData.HozOrgan, pList.Name,\
                       pList.FirstName, pList.MidName, pList.TabNumber,\
                       AcessPoint.Name as 'AcessPointName',\
                       Events.Contents  + DBO.AddState(tpRzdIndex) as 'Contents',\
                       pLogData.Mode, pLogData.DoorIndex, pPost.Name as 'PostName',\
                       pDivision.Name as 'DivisionName'\
                       FROM AcessPoint, pLogData\
               LEFT JOIN pList ON (pLogData.HozOrgan = pList.ID)\
               LEFT JOIN Events ON (pLogData.Event = Events.Event)\
               LEFT JOIN pPost ON (pList.Post = pPost.ID)\
               LEFT JOIN pDivision ON (pList.Section = pDivision.ID)\
               WHERE Plogdata.TimeVal BETWEEN ? AND ?\
               AND pLogData.DoorIndex = AcessPoint.GIndex\
               AND tpIndex IN (8,12)\
               ORDER BY pLogData.DoorIndex,Plogdata.TimeVal;", (date_start, date_end)
               )
    return db


# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.message import EmailMessage

def MailSend():
    textfile = "textfile"
    # Open the plain text file whose name is in textfile for reading.
    with open(textfile) as fp:
        # Create a text/plain message
        msg = EmailMessage()
        msg.set_content(fp.read())

    # me == the sender's email address
    me = "denis@localhost.localdomain"
    # you == the recipient's email address
    you = "denis@localhost.localdomain"
    msg['Subject'] = f'The contents of {textfile}'
    msg['From'] = me
    msg['To'] = you

    # Send the message via our own SMTP server.
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()
    return "ok"

# def users():
#     from flask import Flask
#     from db import get_db
#     db = get_db()
#     cursor = db.execute("SELECT username, IsAdmin FROM user;")
#     r = cursor.fetchone()
#     while r:
#         for i in r:
#             print(i)
#         r = cursor.fetchone()
#     return 'ok'

# import xlsxwriter
# from datetime import datetime
# import os
# from reports_sql import dt
#
# def xlsxReport(date_start, date_end, data, report_name):
#     filename = os.path.join(os.path.abspath('../instance/xlsx'), f"{report_name}_{date_end}_{date_start}.xlsx")
#     workbook = xlsxwriter.Workbook(filename)
#     worksheet = workbook.add_worksheet()
#     # Protect worksheet
#     worksheet.protect()
#     # Sheet heading
#     # Merge format
#     merge_format = workbook.add_format({'align': 'left', 'bold': True, 'font_size': 12})
#     heading = f"Report name: {report_name}\nTime range: from: {dt(date_start)} to: {dt(date_end)}"
#     worksheet.merge_range(1, 4, 2, 8, heading, merge_format)
#     # Insert logo
#     # Merge format
#     merge_format = workbook.add_format({'align': 'center'})
#     image = worksheet.insert_image(0, 0, os.path.join(os.path.abspath('static'), 'logo.png'),
#                             {'x_scale': 0.6, 'y_scale': 0.6,
#                              })
#     worksheet.merge_range(0, 0, 5, 1, image, merge_format)
#     # Keep track columns width
#     col_width = list(range(len(data[0])))
#     # Write data
#     indent = 6
#     old = None
#     for row in range(indent, len(data) + indent):
#         # Head format
#         if row == indent:
#             cell_format = workbook.add_format({'bold': True, 'font_size': 11,
#                             'border': True, 'align': 'center', 'bg_color': '#3b3a30',
#                             'font_color': 'white'})
#         # Highlight every new record in first column
#         elif data[row - indent][0] != old:
#             cell_format = workbook.add_format({'top': True,
#                           'bg_color': '#b2b2b2', 'bold': True,
#                           'num_format': 'dd-mm-yyyy hh:mm:ss',
#                           'align': 'left'})
#             old = data[row - indent][0]
#         # cell
#         else:
#             cell_format = workbook.add_format({'num_format': 'dd-mm-yyyy hh:mm:ss',
#                             'align': 'left', 'right': True,
#                             'left': True, 'bg_color': '#e0e2e4'})
#         for col in range(len(data[row - indent])):
#             if col_width[col] < len(str(data[row - indent][col])):
#                 col_width[col] = len(str(data[row - indent][col]))
#             worksheet.write(row, col, data[row - indent][col], cell_format)
#
#     # Set columns width
#     for col in range(len(col_width)):
#         worksheet.set_column(col, col, col_width[col])
#
#     workbook.close()
#     return f"{report_name}_{date_end}_{date_start}.xlsx"



# import asyncio
#
# timelist = [5, 5, 5]
#
#
# async def func(delay):
#      await asyncio.sleep(delay)
#      print(f"time: {delay}")
#      timelist.remove(delay)
#      timelist.append(timelist[-1] + 5)
#      print(timelist)
#
# async def main():
#     while timelist:
#         timelist.sort()
#         new_tl = []
#         new_tl.append(timelist[0])
#         for i in range(len(timelist) - 1):
#             if timelist[i] == timelist[i + 1]:
#                 new_tl.append(timelist[i + 1])
#
#         tasks = [asyncio.create_task(func(i)) for i in new_tl]
#         for i in range(len(tasks)):
#             await tasks[i]
#
# asyncio.run(main())



        # def create_mail_task():
        #     from datetime import datetime, timedelta
        #     from calendar import day_name
        #
        #
        #     class MailTask:
        #         def __init__(self, id, report_id, recipient, periodicity, time, weekday=None, date=None):
        #             self.id = id
        #             self.report_id = report_id
        #             self.recipient = recipient
        #             self.periodicity = periodicity
        #             self.weekday = weekday
        #             self.date = date
        #             self.time = time
        #
        #     db = get_db()
        #     cursor = db.execute("SELECT id, report_id, recipient, periodicity, time,\
        #                         weekday, date FROM mail_task;")
        #     row = cursor.fetchone()
        #     week_days = list(day_name)
        #     now = datetime.now()
        #     while row:
        #         tuple(row)
        #         print(row)
        #         print(row.keys())
        #         mail_task = MailTask(row['id'], row['report_id'], row['recipient'],
        #                         row['periodicity'], row['time'], row['weekday'],
        #                         row['date'])
        #         print (mail_task.periodicity)
        #         # if mail_task.periodicity == 'daily':
        #         #     pass
        #         if mail_task.periodicity == 'weekly':
        #             print('Y')
        #             # To datetime format
        #             t = datetime.strptime(mail_task.time, '%H:%M:%S').time()
        #             # Count days
        #             days = (week_days.index(mail_task.weekday) - datetime.weekday(now) + 7) % 7
        #             # Count timedelta
        #             countdown = timedelta(days=days, hours=t.hour, minutes=t.minute, seconds=t.second)
        #         # elif mail_task.periodicity == 'monthly':
        #         #     pass
        #         send_mail_task.apply_async(mail_task, countdown=countdown)
        #
        #         row = cursor.fetchone()
        #         print(row)
        #     return
