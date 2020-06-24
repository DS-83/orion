import os
import logging
import time

from flask import Flask, redirect, render_template, request, session
from . import (db, auth, orion, reports, reports_sql, xlsx_, admin,
                sendemail
              )
from celery import Celery

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=b'^SD$%1D<<L^Ggn97d5c3@!b94',
        DATABASE=os.path.join(app.instance_path, 'app.sqlite'),
        DWNLD_FOLDER=os.path.join(app.instance_path, 'xlsx'),
        LOGS_FOLDER=os.path.join(app.instance_path, 'logs'),
        CELERY_BROKER_URL='redis://localhost:6379',
        CELERY_RESULT_BACKEND='redis://localhost:6379'

    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Register DB access
    db.init_app(app)

    # Register Auth Blueprint
    app.register_blueprint(auth.bp)

    # Main App Orion
    app.register_blueprint(orion.bp)
    app.add_url_rule('/', endpoint='index')

    # Register Reporsts Blueprint
    app.register_blueprint(reports.bp)

    # Register Admin Blueprint
    app.register_blueprint(admin.bp)

    celery = make_celery(app)


    # Logging config
    logger = logging.getLogger(__name__)
    logfile = f"{app.config['LOGS_FOLDER']}/app-{time.strftime('%Y%m%d')}.log"
    logging.basicConfig(filename=logfile, level=logging.INFO)
    logging.info('Started')

    return app
