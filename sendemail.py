# Import smtplib for the actual sending function
import smtplib
# Import the email modules we'll need
from email.message import EmailMessage
import logging
import os
from time import strftime
import sqlite3


SERVER = "localhost"
PORT = 25


# Logging config
logger = logging.getLogger(__name__)
logfile = os.path.join(os.path.abspath('instance/logs'), f"mail-{strftime('%Y%m%d')}.log")
logging.basicConfig(filename=logfile, level=logging.INFO)


# DB
def get_db():
    db = sqlite3.connect(
        os.path.join('./instance', 'app.sqlite'),
        detect_types=sqlite3.PARSE_DECLTYPES
    )
    db.row_factory = sqlite3.Row

    return db


# Function for testing connection
def test_smtp(server, port):
    with smtplib.SMTP(server, port) as s:
        r = s.noop()
        if r[0] == 250 and r[1].lower() == b'2.0.0 ok':
            return True, (250, b'2.0.0 Ok')
    return False

def send_mail():
    textfile = "textfile"
    xlsxfile = "Bro_20191203140000_20191202110100.xlsx"
    # Open the plain text file whose name is in textfile for reading.
    with open(textfile) as fp:
        # Create a text/plain message
        msg = EmailMessage()
        msg.set_content(fp.read())

    # me == the sender's email address
    me = "denis@localhost"
    # you == the recipient's email address
    you = "denis@localhost"
    msg['Subject'] = f"The contents of {textfile}"
    msg['From'] = me
    msg['To'] = you
    # Create xlsx attach
    with open(xlsxfile, 'rb') as fp:
        xlsx_data = fp.read()
    msg.add_attachment(xlsx_data,
        'application',
        'vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        filename = xlsxfile)

    # Get config from DB
    db = get_db()
    config = db.execute("SELECT server, port FROM smtp;").fetchone()
    if config:
        SERVER = config[0]
        PORT = config[1]
    # Send the email via our own SMTP server.
    with smtplib.SMTP(SERVER, PORT) as smtp:
        smtp.send_message(msg)

    return "ok"

class SendMail:
    def __init__(self, text, xlsxfile, sender, to, subj):
        self.text = text
        self.xlsxfile = xlsxfile
        self.sender = sender
        self.to = to
        self.subj = subj

    def start(self):
        # Open the plain text file whose name is in textfile for reading.
        with open(self.text) as fp:
            # Create a text/plain message
            msg = EmailMessage()
            msg.set_content(fp.read())
        msg['From'] = self.sender
        msg['To'] = self.to
        # Create xlsx attach
        with open(self.xlsxfile, 'rb') as fp:
            xlsx_data = fp.read()
        msg.add_attachment(xlsx_data,
            'application',
            'vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            filename = self.xlsxfile)

        # Get config from DB
        db = get_db()
        config = db.execute("SELECT server, port FROM smtp;").fetchone()
        if config:
            SERVER = config[0]
            PORT = config[1]
        # Send the email via our own SMTP server.
        with smtplib.SMTP(SERVER, PORT) as smtp:
            smtp.send_message(msg)
            logging.info(f'msg to {self.to} successfuly send. mail-server: {SERVER}:{PORT}')
            return True

        logging.error(f'error sending mail msg {self.to}, server: {SERVER}:{PORT}')
        return False
