import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

import pyodbc

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

# MS SQL Server connection

# Some other example server values are
# server = 'localhost\sqlexpress' # for a named instance
# server = 'myserver,port' # to specify an alternate port

# conn.commit() will automatically be called when Python leaves the outer `with` statement
# Neither crs.close() nor conn.close() will be called upon leaving the the `with` statement!!
def get_mssql():
    if 'odbcConn' not in g:
        server = '192.168.0.55'
        database = 'Orionnew'
        username = 'sa'
        password = '123456'

        g.odbcConn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
        g.cursor = g.odbcConn.cursor()
    return g.cursor
