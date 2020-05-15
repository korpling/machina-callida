from typing import Type

from flask import Flask
from graphannis.cs import CorpusStorageManager

from mcserver import Config
from mcserver.app import init_app_common, init_logging


def create_csm_app(cfg: Type[Config] = Config) -> Flask:
    """Creates a new Flask app that represents a Corpus Storage Manager."""

    Config.CORPUS_STORAGE_MANAGER = CorpusStorageManager(Config.GRAPH_DATABASE_DIR)
    app_csm: Flask = init_app_common(cfg=cfg, is_csm=True)
    from csm.app.api import bp
    app_csm.register_blueprint(bp)
    init_logging(app_csm, Config.LOG_PATH_CSM)
    return app_csm
