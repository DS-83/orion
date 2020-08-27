# Import smtplib for the actual sending function
import smtplib
# Import the email modules we'll need
from email.message import EmailMessage
import logging
import os
from time import strftime
from flask import url_for
from app.db import get_db_no_g, get_db

from flask_babel import _


# Default configuration
SERVER = "localhost"
PORT = 25


# Logging config
logfile = os.path.join(os.path.abspath('instance/logs'), f"mail-{strftime('%Y%m%d')}.log")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# create file handler which logs even debug messages
fh = logging.FileHandler(logfile)
fh.setLevel(logging.INFO)
# # create console handler with a higher log level
# ch = logging.StreamHandler()
# ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# ch.setFormatter(formatter)
fh.setFormatter(formatter)
# add the handlers to logger
# logger.addHandler(ch)
logger.addHandler(fh)


# Function for testing connection
def test_smtp(server, port):
    try:
        with smtplib.SMTP(server, port) as s:
            r = s.noop()
        if r[0] == 250 and r[1].lower() == b'2.0.0 ok':
            return True, (250, b'2.0.0 Ok')
    except Exception as err:
        return False, err

# Class for create and send mail
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
        msg['Subject'] = self.subj
        # Create xlsx attach
        with open(self.xlsxfile, 'rb') as fp:
            xlsx_data = fp.read()
        msg.add_attachment(xlsx_data,
            'application',
            'vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            filename = self.xlsxfile)

        # Get config from DB
        db = get_db_no_g()
        config = db.execute("SELECT server, port FROM smtp;").fetchone()
        if config:
            SERVER = config[0]
            PORT = config[1]
        # Send the email via our own SMTP server.
        with smtplib.SMTP(SERVER, PORT) as smtp:
            smtp.send_message(msg)
            logger.info(f'Msg to: {self.to} successfuly send. Mail-server: {SERVER}:{PORT}')
            return True

        logger.error(f'Error sending mail msg to: {self.to}, server: {SERVER}:{PORT}')
        return False


class SendMailResetPassword:
    def __init__(self, sender, to, token):
        self.sender = sender
        self.to = to
        self.token = token

    def start(self):
        msg_body = f"""You recently requested to reset password for your account.
                    Use the button below to reset it.
                    {url_for('orion.reset_password', token=self.token, _external=True)}"""
        msg = EmailMessage()
        msg.set_content(msg_body)
        msg['From'] = self.sender
        msg['To'] = self.to
        msg['Subject'] = _("Automatic mail. Reset password OrionNG report system")
        msg.add_alternative(f"""
        <!DOCTYPE html>
        <html>
          <head>
            <meta charset="utf-8">
            <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css>
             <style>
               @media (max-width: 991.98px){'{}'}
             </style>
          </head>
          <body>
            <div class="container-sm p-3">
              <h4 class="h4">Reset password</h4>
            </div>
            <div class="container-sm p-3">
              You recently requested to reset password for your account.
              Use the button below to reset it.
              <strong>This password reset is only valid
              for the next 1 hour.</strong>
            </div>
            <div class="container container-sm">
              <a class="btn btn-success btn-lg" href='{url_for('orion.reset_password', token=self.token, _external=True)}' role="button">Reset password</a>
            </div>
          </body>
        </html>
        """, subtype='html')

        db = get_db()
        config = db.execute("SELECT server, port FROM smtp;").fetchone()
        if config:
            SERVER = config[0]
            PORT = config[1]
        # Send the email via our own SMTP server.
        with smtplib.SMTP(SERVER, PORT) as smtp:
            smtp.send_message(msg)
            logger.info(f'Reset password message to: {self.to} successfuly send. Mail-server: {SERVER}:{PORT}')
            return True

        logger.error(f'Error sending mail msg to: {self.to}, server: {SERVER}:{PORT}')
        return False
