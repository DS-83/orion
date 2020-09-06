import os
import logging
import time

from flask import Flask, redirect, render_template, request, session, url_for
from . import db, auth, orion, reports,  admin

from flask_babel import Babel
from app import config_module


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=b'^SD$%1D<<L^Ggn97d5c3@!b94',
        LOGS_FOLDER=os.path.join(app.instance_path, 'logs'),
        DWNLD_FOLDER=os.path.join(app.instance_path, 'xlsx'),
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

    # Ensure the instance folder exists
    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)
    if not os.path.exists(app.config['LOGS_FOLDER']):
        os.makedirs(app.config['LOGS_FOLDER'])
    if not os.path.exists(app.config['DWNLD_FOLDER']):
        os.makedirs(app.config['DWNLD_FOLDER'])
    if not os.path.exists(app.config['TEXTFILE_FOLDER']):
        os.makedirs(app.config['TEXTFILE_FOLDER'])

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
    logdir = app.config['LOGS_FOLDER']
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_level = logging.INFO
    for logger in (
        app.logger,
        logging.getLogger('app.admin'),
        logging.getLogger('app.orion'),
        logging.getLogger('app.sendemail'),
        logging.getLogger('app.auth')

    ):
        log_file = os.path.join(logdir,  f"{logger.name}-{time.strftime('%Y%m%d')}.log")
        handler = logging.FileHandler(log_file)
        handler.setLevel(log_level)
        logger.setLevel(log_level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)


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

    app.logger.info('App started')

    return app
