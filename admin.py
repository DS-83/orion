from flask import (Blueprint, render_template, request,
        flash, redirect, url_for, g, current_app)
from app.auth import login_required, user_role, user_first_logon
from app.sendemail import test_smtp, SendMailResetPassword
from app.db import get_db, test_mssql
from werkzeug.security import generate_password_hash

import os

from time import strftime

import logging

from cryptography.fernet import Fernet

from flask_babel import _

from app.serializer import get_reset_token


# Logging config
logger = logging.getLogger(__name__)


bp = Blueprint('admin', __name__, url_prefix='/admin')

# Add administrative views here
@bp.route('/')
@login_required
@user_role
@user_first_logon
def index():
    return render_template('admin/admin.html')

# Route SMTP server configure
@bp.route('/smtpconf', methods=('GET', 'POST'))
@login_required
@user_role
@user_first_logon
def smtpconf():

    db = get_db()
    config = db.execute("SELECT server, port, ssl FROM smtp;").fetchone()

    if request.method == 'POST':
        # Test connection to smtp server
        if request.form['submit'] == 'test':
            server = request.form.get('smtpserver')
            port = request.form.get('port')
            r = test_smtp(server, port)
            if r[0]:
                flash(f"{_('Success')}. {r[1]}", 'success')
            else:
                flash(f"{_('Faled')}. {r[1]}", 'danger')
            return render_template('admin/smtpconf.html', config=config)

        # Save smtp config to DB
        if request.form['submit'] == 'save':
            server = request.form.get('smtpserver')
            port = request.form.get('port')
            ssl = request.form.get('ssl')
            if ssl == "on":     # 'on' if checked
                ssl = 1
            else:
                ssl = 0
            username = request.form.get('username')
            password = request.form.get('password')
            try:
                if config is None:
                    db.execute("INSERT INTO smtp (server, port, ssl, username, password)\
                                VALUES (?,?,?,?,?);", (server, port, ssl, username, password))
                else:
                    db.execute("UPDATE smtp SET server=?, port=?, ssl=?, username=?,\
                                password=? WHERE id = 1;", (server, port, ssl, username, password))
                db.commit()
                flash(_('Saved'), 'success')
                logger.info(f"SMTP config was change by user {g.user['username']}")
                config = db.execute("SELECT server, port, ssl FROM smtp;").fetchone()

            except Exception as err:
                flash(err)
                logger.warning(err)

    return render_template('admin/smtpconf.html', config=config)

# Route Users
@bp.route('/users', methods=('GET', 'POST'))
@login_required
@user_role
@user_first_logon
def users():

    try:
        # Get users from DB
        db = get_db()
        cursor = db.execute(
            "SELECT username, firstname, lastname,\
            email, company, IsAdmin as 'Admin', status, id  FROM user;")
        row = cursor.fetchone()
        # Make list
        users = []
        users.append(row.keys())
        while row:
            users.append(list(row))
            row = cursor.fetchone()
        # Replace numbers with "Yes" or "No"
        for user in users:
            if user[5] == 1:
                user[5] = 'Yes'
            elif user[5] == 0:
                user[5] = 'No'
    except:
        users = None

    # Route for 'POST'
    if request.method == "POST":

        error = None

        # Edit user
        if request.form['submit'] == 'edit':
            username = request.form['username']
            if not username:
                error = _('USERNAME can not be blank')

            else:
                username = username[0].upper() + request.form['username'][1:].lower()

                if username == 'Admin':
                    error = _("Name 'Admin' already taken. Select another USERNAME")

            if error is None:
                firstname = request.form.get('Firstname')
                lastname = request.form.get('Lastname')
                email = request.form.get('Email')
                company = request.form.get('Company')
                admin = request.form.get('Admin')
                status = request.form['status']
                if admin == "Yes":
                    admin = 1
                else:
                    admin = 0
                id = request.form.get('hidden_id')
                try:
                    db.execute("UPDATE user SET username=?, firstname=?, lastname=?,\
                        email=?, company=?, IsAdmin=?, status=? WHERE id = ?",
                        (username, firstname, lastname, email, company, admin, status, id)
                    )
                    db.commit()
                    flash(_('Saved'), 'success')
                    logger.info(f"User account {username} was change by user {g.user['username']}")
                    return redirect(url_for('.users'))
                except Exception as error:
                    logger.warning(error)

        # New user
        if request.form['submit'] == 'new':
            username = request.form['username']
            if not username:
                error = _('USERNAME can not be blank')

            else:
                username = username[0].upper() + request.form['username'][1:].lower()

                if username == 'Admin':
                    error = _("Name 'Admin' already taken. Select another USERNAME")
                elif users:
                    for user in users:
                        if username == user[0]:
                            error = _("Username %(u)s already taken", u = username)

            if error is None:
                password = request.form['password']

                if not password:
                    error = _('<password> can not be blank')
                else:
                    password = generate_password_hash(password)
                    firstname = request.form.get('Firstname')
                    lastname = request.form.get('Lastname')
                    email = request.form.get('Email')
                    company = request.form.get('Company')
                    admin = request.form.get('Admin')
                    if admin == "Yes":
                        admin = 1
                    else:
                        admin = 0
                    try:
                        db.execute("INSERT INTO user\
                            (username, password, firstname, lastname, email, company, IsAdmin)\
                            VALUES (?,?,?,?,?,?,?);",\
                            (username, password, firstname, lastname, email, company, admin)
                        )
                        db.commit()
                        flash(_('User added'), 'success')
                        logger.info(f"Create new user {username}, by user {g.user['username']}")
                        return redirect(url_for('.users'))
                    except Exception as error:
                        logger.warning(error)

        # Reset user password
        if request.form['submit'] == 'reset':
            user_id = request.form['hidden_id_disp']
            if user_id is None:
                error = _('Internal server error')
            else:
                cursor = db.execute('SELECT email, username FROM user WHERE id = ?',
                                    (user_id,)
                                 ).fetchone()
                token = get_reset_token(user_id)
                mail_obj = SendMailResetPassword(current_app.config['MAIL_SENDER'],
                                                 cursor['email'], token)
                if mail_obj.start():
                    flash(_('Email with instructions was successfuly sent to user %(u)s',
                            u=cursor['username']), 'success')
                    logger.info(f"Reset password email was sent to user {cursor['username']}, by {g.user['username']}")
                    return render_template('admin/users.html', users=users)
                else:
                    error = _('Error sending email message')
        flash(error, 'warning')

    return render_template('admin/users.html', users=users)


# Route MSSQL server connection configure
@bp.route('/mssqlconf', methods=('GET', 'POST'))
@login_required
@user_role
@user_first_logon
def mssqlconf():

    db = get_db()
    config = db.execute("SELECT server, database, username FROM mssql").fetchone()

    if request.method == 'POST':

        server = request.form['MSSQLserver']
        database = request.form['database']
        username = request.form['username']
        password = request.form['password']

        # Encrypt password
        key = current_app.config['KEY_P']
        cipher_suite = Fernet(key)
        ciphered_text = cipher_suite.encrypt(str.encode(password))

        # Test connection to mssql server
        if request.form['submit'] == 'test':
            r = test_mssql(server, database, username, password)
            if r[0]:
                flash(_("Success. %(msg)s", msg = r[1]), 'success')
            else:
                flash(_("Faled. %(msg)s", msg = r[1]), 'danger')
            return render_template('admin/mssqlconf.html', config=config)

        # Save mssql config to DB
        if request.form['submit'] == 'save':

            try:
                if config is None:
                    db.execute("INSERT INTO mssql (server, database, username, password)\
                                VALUES (?,?,?,?);", (server, database, username, ciphered_text))
                else:
                    db.execute("UPDATE mssql SET server=?, database=?, username=?,\
                                password=? WHERE id = 1;", (server, database, username, ciphered_text))
                db.commit()

                flash(_('Saved'), 'success')

                logger.info(f"MSSQL config was change by user {g.user['username']}")

                config = db.execute("SELECT server, database, username FROM mssql;").fetchone()

            except Exception as err:
                flash(err)
                logger.warning(err)


    return render_template('admin/mssqlconf.html', config=config)
