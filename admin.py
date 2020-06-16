from flask import Blueprint, render_template, request, flash
from app.auth import login_required, user_role
from app.sendemail import Test
from app.db import get_db


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
    if request.method == 'POST':
        db = get_db()
        config = db.execute("SELECT server, port, ssl FROM smtp;").fetchone()
        # Test connection to smtp server
        if request.form['submit'] == 'test':
            server = request.form.get('smtpserver')
            port = request.form.get('port')
            r = Test(server, port)
            flash(f"Success {r[1]}")
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
                flash('Saved')
                config = db.execute("SELECT server, port, ssl FROM smtp;").fetchone()
                return render_template('admin/smtpconf.html', config=config)

            except Exception as err:
                flash(err)
                return render_template('admin/smtpconf.html', config=config)


    db = get_db()
    config = db.execute("SELECT server, port, ssl FROM smtp;").fetchone()
    return render_template('admin/smtpconf.html', config=config)
