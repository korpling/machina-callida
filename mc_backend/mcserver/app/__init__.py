"""The main module for the application. It contains the application factory and provides access to the database."""
import logging
import sys
from logging.handlers import RotatingFileHandler
from threading import Thread
from time import strftime
from typing import Type
from flask import Flask, got_request_exception, request, Response
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from mcserver.config import Config

db: SQLAlchemy = SQLAlchemy()  # session_options={"autocommit": True}
migrate: Migrate = Migrate(directory=Config.MIGRATIONS_DIRECTORY)


def create_app(cfg: Type[Config] = Config) -> Flask:
    """Create a new Flask application and configure it. Initialize the application and the database.
    Arguments:
        cfg -- the desired configuration class for the application
    """
    # use local postgres database for migrations
    if len(sys.argv) > 2 and sys.argv[2] == Config.FLASK_MIGRATE:
        cfg.SQLALCHEMY_DATABASE_URI = Config.DATABASE_URL_LOCAL
    app = init_app_common(cfg=cfg)
    from mcserver.app.services import bp as services_bp
    app.register_blueprint(services_bp)
    from mcserver.app.api import bp as api_bp
    app.register_blueprint(api_bp)
    init_logging(app, Config.LOG_PATH_MCSERVER)
    return app


def full_init(app: Flask, is_csm: bool) -> None:
    """ Fully initializes the application, including logging."""
    from mcserver.app.services.corpusService import CorpusService
    from mcserver.app.services import CustomCorpusService
    if is_csm:
        from mcserver.app.services.databaseService import DatabaseService
        DatabaseService.init_db_update_info()
        DatabaseService.update_exercises(is_csm=is_csm)
        DatabaseService.init_db_corpus()
        if not app.config["TESTING"]:
            CorpusService.init_graphannis_logging()
            start_updater(app)


def init_app_common(cfg: Type[Config] = Config, is_csm: bool = False) -> Flask:
    """ Initializes common Flask parts, e.g. CORS, configuration, database, migrations and custom corpora."""
    app = Flask(__name__)

    @app.after_request
    def after_request(response: Response) -> Response:
        """ Logs metadata for every request. """
        timestamp = strftime('[%Y-%m-%d %H:%M:%S]')
        app.logger.info('%s %s %s %s %s %s', timestamp, request.remote_addr, request.method, request.scheme,
                        request.full_path, response.status)
        return response

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        """ Shuts down the session when the application exits. (maybe also after every request ???) """
        db.session.remove()

    # allow CORS requests for all API routes
    CORS(app)  # , resources=r"/*"
    app.config.from_object(cfg)
    app.app_context().push()
    db.init_app(app)
    migrate.init_app(app, db)
    db.create_all()
    from mcserver.app.services.databaseService import DatabaseService
    DatabaseService.init_db_alembic()
    from mcserver.app.services.textService import TextService
    TextService.init_proper_nouns_list()
    TextService.init_stop_words_latin()
    full_init(app, is_csm)
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


def log_exception(sender_app: Flask, exception, **extra):
    """Logs errors that occur while the Flask app is working.

    Arguments:
        sender_app -- the Flask application
        exception -- the exception to be logged
        **extra -- any additional arguments
    """
    # TODO: RETURN ERROR IN JSON FORMAT
    sender_app.logger.exception("ERROR")


def start_updater(app: Flask) -> Thread:
    """ Starts a new Thread for to perform updates in the background. """
    from mcserver.app.services import DatabaseService
    t = Thread(target=DatabaseService.init_updater, args=(app,))
    t.daemon = True
    t.start()
    return t


# import the models so we can access them from other parts of the app using imports from "app.models";
# this has to be at the bottom of the file
from mcserver.app import models
