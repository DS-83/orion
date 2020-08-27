import os
import logging
import time

from flask import Flask, redirect, render_template, request, session, url_for
from . import (db, auth, orion, reports, reports_sql, xlsx_, admin,
                sendemail, celery_utils, tasks
              )

from flask_babel import Babel


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=b'^SD$%1D<<L^Ggn97d5c3@!b94',
        DWNLD_FOLDER=os.path.join(app.instance_path, 'xlsx'),
        LOGS_FOLDER=os.path.join(app.instance_path, 'logs'),
        TEXTFILE_FOLDER=os.path.join(app.instance_path, 'textmsg'),
        MAIL_SENDER='orion@localhost'

    )
    app.config.from_object('config_module.ProductionConfig')

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

    babel = Babel(app)

    # Logging config
    logger = logging.getLogger(__name__)
    logfile = f"{app.config['LOGS_FOLDER']}/app-{time.strftime('%Y%m%d')}.log"
    logging.basicConfig(filename=logfile, level=logging.INFO)
    logger.setLevel(logging.INFO)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(logfile)
    fh.setLevel(logging.INFO)
    # create console handler with a higher log level
    # ch = logging.StreamHandler()
    # ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    # add the handlers to logger
    # logger.addHandler(ch)
    logger.addHandler(fh)

    logger.info('App started')


    @app.route('/language/<language>')
    def set_language(language=None):
        session['language'] = language

        # Redirect back to the url that came from
        return redirect(request.referrer)


    @babel.localeselector
    def get_locale():
        # if the user has set up the language manually it will be stored in the session,
        # so we use the locale from the user settings
        try:
            language = session['language']
        except KeyError:
            language = None
        if language is not None:
            return language
        return request.accept_languages.best_match(app.config['LANGUAGES'].keys())

    @app.context_processor
    def inject_conf_var():
        return dict(
                    AVAILABLE_LANGUAGES=app.config['LANGUAGES'],
                    CURRENT_LANGUAGE=session.get('language',
                    request.accept_languages.best_match(app.config['LANGUAGES'].keys())))



    return app
