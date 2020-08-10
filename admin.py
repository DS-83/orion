from flask import (Blueprint, render_template, request,
        flash, redirect, url_for)
from app.auth import login_required, user_role
from app.sendemail import test_smtp
from app.db import get_db, test_mssql
from werkzeug.security import generate_password_hash



# # set optional bootswatch theme
# app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

bp = Blueprint('admin', __name__, url_prefix='/admin')

# Add administrative views here
@bp.route('/')
@login_required
@user_role
def index():
    return render_template('admin/admin.html')

# Route SMTP server configure
@bp.route('/smtpconf', methods=('GET', 'POST'))
@login_required
@user_role
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
                flash(f"Success {r[1]}", 'success')
            else:
                flash(f"Faled. {r[1]}", 'danger')
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
                flash('Saved', 'success')
                config = db.execute("SELECT server, port, ssl FROM smtp;").fetchone()
                return render_template('admin/smtpconf.html', config=config)

            except Exception as err:
                flash(err)
                return render_template('admin/smtpconf.html', config=config)


    return render_template('admin/smtpconf.html', config=config)

# Route Users
@bp.route('/users', methods=('GET', 'POST'))
@login_required
@user_role
def users():

    # Get users from DB
    db = get_db()
    cursor = db.execute(
        "SELECT username as 'Username', firstname, lastname,\
        email, company, IsAdmin as 'Admin', status, id  FROM user;")
    row = cursor.fetchone()
    # Make list`
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


    # Route for 'POST'
    if request.method == "POST":

        # Edit user
        if request.form['submit'] == 'edit':
            username = request.form['username']
            if not username:
                flash("<username> can not be blank")
                return render_template('admin/users.html', users=users)
            username = username[0].upper() + request.form['username'][1:].lower()
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
                flash('saved', 'success')
                return redirect(url_for('.users'))
            except Exception as err:
                flash(err, 'warning')
                return render_template('admin/users.html', users=users)

        # New user
        if request.form['submit'] == 'new':
            username = request.form['username']
            if not username:
                flash('<username> can not be blank', 'warning')
                return render_template('admin/users.html', users=users)
            username = username[0].upper() + request.form['username'][1:].lower()
            for user in users:
                if username == user[0]:
                    flash(f'Username {username} already taken', 'warning')
                    return render_template('admin/users.html', users=users)
            password = request.form['password']
            if not password:
                flash('<password> can not be blank', 'warning')
                return render_template('admin/users.html', users=users)
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
                flash('User added', 'success')
                return redirect(url_for('.users'))
            except Exception as err:
                flash(err)
                return render_template('admin/users.html', users=users)



    return render_template('admin/users.html', users=users)


# Route MSSQL server connection configure
@bp.route('/mssqlconf', methods=('GET', 'POST'))
@login_required
@user_role
def mssqlconf():

    db = get_db()
    config = db.execute("SELECT server, database, username FROM mssql").fetchone()

    if request.method == 'POST':

        server = request.form['MSSQLserver']
        database = request.form['database']
        username = request.form['username']
        password = request.form['password']

        # Test connection to mssql server
        if request.form['submit'] == 'test':
            r = test_mssql(server, database, username, password)
            if r[0]:
                flash(f"Success. {r[1]}", 'success')
            else:
                flash(f"Faled. {r[1]}", 'danger')
            return render_template('admin/mssqlconf.html', config=config)

        # Save mssql config to DB
        if request.form['submit'] == 'save':

            try:
                if config is None:
                    db.execute("INSERT INTO mssql (server, database, username, password)\
                                VALUES (?,?,?,?);", (server, database, username, password))
                else:
                    db.execute("UPDATE mssql SET server=?, database=?, username=?,\
                                password=? WHERE id = 1;", (server, database, username, password))
                db.commit()
                flash('Saved', 'success')
                config = db.execute("SELECT server, database, username FROM mssql;").fetchone()

            except Exception as err:
                flash(err)


    return render_template('admin/mssqlconf.html', config=config)
