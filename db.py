import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

import pyodbc

import os

from cryptography.fernet import Fernet

from config_module import Config


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


# Without context
def get_db_no_g():
    db = sqlite3.connect(
        os.path.join('./instance', 'app.sqlite'),
        detect_types=sqlite3.PARSE_DECLTYPES
    )
    db.row_factory = sqlite3.Row

    return db

# MS SQL Server connection

# Some other example server values are
# server = 'localhost\sqlexpress' # for a named instance
# server = 'myserver,port' # to specify an alternate port

# conn.commit() will automatically be called when Python leaves the outer `with` statement
# Neither crs.close() nor conn.close() will be called upon leaving the the `with` statement!!
def get_mssql():

    row = get_db().execute("SELECT * FROM mssql").fetchone()
    SERVER = row['server']
    DATABASE = row['database']
    USERNAME = row['username']
    ciphered_text = row['password']

    # Uncipher password
    key = current_app.config['KEY_P']
    cipher_suite = Fernet(key)
    uncipher_text = (cipher_suite.decrypt(ciphered_text))
    PASSWORD = bytes(uncipher_text).decode("utf-8")

    if 'odbcConn' not in g:

        g.odbcConn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};\
                                     SERVER='+SERVER+';DATABASE='+DATABASE+';\
                                     UID='+USERNAME+';PWD='+ PASSWORD)
        g.cursor = g.odbcConn.cursor()
    return g.cursor


def get_mssql_no_g():

    row = get_db_no_g().execute("SELECT * FROM mssql").fetchone()
    SERVER = row['server']
    DATABASE = row['database']
    USERNAME = row['username']
    ciphered_text = row['password']

    # Uncipher password
    cipher_suite = Fernet(Config.KEY_P)
    uncipher_text = (cipher_suite.decrypt(ciphered_text))
    PASSWORD = bytes(uncipher_text).decode("utf-8")

    odbcConn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};\
                               SERVER='+SERVER+';DATABASE='+DATABASE+';\
                               UID='+USERNAME+';PWD='+ PASSWORD)
    cursor = odbcConn.cursor()
    return cursor


# Function for testing connection to mssql server
def test_mssql(server, database, username, password):
    try:
        with pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};\
                                        SERVER='+server+';DATABASE='+database+';\
                                        UID='+username+';PWD='+ password) as odbcConn:

            cursor = odbcConn.cursor()
            if isinstance(cursor, pyodbc.Cursor):
                #select query
                result = ""
                cursor.execute("SELECT @@version;")
                row = cursor.fetchone()
                while row:
                    result += row[0]
                    row = cursor.fetchone()
                return True, result

    except Exception as err:
        return False, err
