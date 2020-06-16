# Import smtplib for the actual sending function
import smtplib
# Import the email modules we'll need
from email.message import EmailMessage

SERVER = "localhost"
PORT = 25

# Function for testing connection
def Test(server, port):
    with smtplib.SMTP(server, port) as s:
        r = s.noop()
        if r[0] == 250 and r[1].lower() == b'2.0.0 ok':
            return True, (250, b'2.0.0 Ok')
    return False

def SendMail():
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


    # Send the email via our own SMTP server.
    with smtplib.SMTP(SERVER, PORT) as smtp:
        smtp.send_message(msg)

    return "ok"
