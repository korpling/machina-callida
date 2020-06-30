"""The main module for the application. It contains the application factory and provides access to the database."""
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from threading import Thread
from time import strftime
from typing import Type
import connexion
import flask
import open_alchemy
import prance
from connexion import FlaskApp
from flask import Flask, got_request_exception, request, Response, send_from_directory
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from open_alchemy import init_yaml
from mcserver.config import Config

db: SQLAlchemy = SQLAlchemy()  # session_options={"autocommit": True}
migrate: Migrate = Migrate(directory=Config.MIGRATIONS_DIRECTORY)
if not hasattr(open_alchemy.models, Config.DATABASE_TABLE_CORPUS):
    # do this _BEFORE_ you add any APIs to your application
    init_yaml(Config.API_SPEC_MODELS_YAML_FILE_PATH, base=db.Model,
              models_filename=os.path.join(Config.MC_SERVER_DIRECTORY, "models_auto.py"))


def apply_event_handlers(app: FlaskApp):
    """Applies event handlers to a given Flask application, such as logging after requests or teardown logic."""

    @app.app.after_request
    def after_request(response: Response) -> Response:
        """ Logs metadata for every request. """
        timestamp = strftime('[%Y-%m-%d %H:%M:%S]')
        app.app.logger.info('%s %s %s %s %s %s', timestamp, request.remote_addr, request.method, request.scheme,
                            request.full_path, response.status)
        return response

    @app.route(Config.SERVER_URI_FAVICON)
    def get_favicon():
        """Sends the favicon to browsers, which is used, e.g., in the tabs as a symbol for our application."""
        mime_type: str = 'image/vnd.microsoft.icon'
        return send_from_directory(Config.ASSETS_DIRECTORY, Config.FAVICON_FILE_NAME, mimetype=mime_type)

    app.app.teardown_appcontext(shutdown_session)


def create_app(cfg: Type[Config] = Config) -> Flask:
    """Create a new Flask application and configure it. Initialize the application and the database.
    Arguments:
        cfg -- the desired configuration class for the application
    """
    # use local postgres database for migrations
    if len(sys.argv) > 2 and sys.argv[2] == Config.FLASK_MIGRATE:
        cfg.SQLALCHEMY_DATABASE_URI = Config.DATABASE_URL_LOCAL
    app: Flask = init_app_common(cfg=cfg)
    from mcserver.app.services import bp as services_bp
    app.register_blueprint(services_bp)
    from mcserver.app.api import bp as api_bp
    app.register_blueprint(api_bp)
    init_logging(app, Config.LOG_PATH_MCSERVER)
    return app


def full_init(app: Flask, cfg: Type[Config] = Config) -> None:
    """ Fully initializes the application, including logging."""
    from mcserver.app.services import DatabaseService
    DatabaseService.init_db_update_info()
    DatabaseService.update_exercises(is_csm=True)
    DatabaseService.init_db_corpus()
    if not cfg.TESTING:
        from mcserver.app.services.corpusService import CorpusService
        CorpusService.init_graphannis_logging()
        start_updater(app)


def init_app_common(cfg: Type[Config] = Config, is_csm: bool = False) -> Flask:
    """ Initializes common Flask parts, e.g. CORS, configuration, database, migrations and custom corpora."""
    spec_dir: str = Config.CSM_DIRECTORY if is_csm else Config.MC_SERVER_DIRECTORY
    connexion_app: FlaskApp = connexion.FlaskApp(
        __name__, port=(cfg.CORPUS_STORAGE_MANAGER_PORT if is_csm else cfg.HOST_PORT), specification_dir=spec_dir)
    spec_path: str = Config.API_SPEC_CSM_FILE_PATH if is_csm else Config.API_SPEC_MCSERVER_FILE_PATH
    parser = prance.ResolvingParser(spec_path, lazy=True, strict=False)  # str(Path(spec_path).absolute())
    parser.parse()
    connexion_app.add_api(parser.specification)
    apply_event_handlers(connexion_app)
    app: Flask = connexion_app.app
    # allow CORS requests for all API routes
    CORS(app)  # , resources=r"/*"
    app.config.from_object(cfg)
    app.app_context().push()
    db.init_app(app)
    migrate.init_app(app, db)
    if is_csm or cfg.TESTING:
        db.create_all()
    if is_csm:
        from mcserver.app.services.databaseService import DatabaseService
        DatabaseService.init_db_alembic()
    from mcserver.app.services.textService import TextService
    TextService.init_proper_nouns_list()
    TextService.init_stop_words_latin()
    if is_csm:
        full_init(app, cfg)
    return app


def init_logging(app: Flask, log_file_path: str):
    """ Initializes logging for a given Flask application. """
    file_handler: RotatingFileHandler = RotatingFileHandler(log_file_path, maxBytes=1000 * 1000,
                                                            backupCount=3)
    log_level: int = logging.INFO
    file_handler.setLevel(log_level)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(log_level)
    got_request_exception.connect(log_exception, app)
    database_uri: str = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    database_uri = database_uri.split('@')[1] if '@' in database_uri else database_uri
    app.logger.warning(f"Accessing database at: {database_uri}")


def log_exception(sender_app: Flask, exception, **extra):
    """Logs errors that occur while the Flask app is working.

    Arguments:
        sender_app -- the Flask application
        exception -- the exception to be logged
        **extra -- any additional arguments
    """
    sender_app.logger.info(f"ERROR for {flask.request.url}")


def start_updater(app: Flask) -> Thread:
    """ Starts a new Thread for to perform updates in the background. """
    from mcserver.app.services import DatabaseService
    t = Thread(target=DatabaseService.init_updater, args=(app,))
    t.daemon = True
    t.start()
    return t


def shutdown_session(exception=None):
    """ Shuts down the session when the application exits. (maybe also after every request ???) """
    db.session.remove()


# import the models so we can access them from other parts of the app using imports from "app.models";
# this has to be at the bottom of the file
from mcserver.app import models
from mcserver.app import api
