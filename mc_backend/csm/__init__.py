"""The main application: Machina Callida.

It is a server-side backend for retrieving Latin texts and
generating language exercises for them."""
import sys
from typing import Type
from flask import Flask
from csm.app import create_csm_app
from mcserver.config import Config, ProductionConfig, DevelopmentConfig, TestingConfig


def get_app() -> Flask:
    return create_csm_app(get_cfg())


def get_cfg() -> Type[Config]:
    return ProductionConfig if Config.IS_PRODUCTION else (
        TestingConfig if len(sys.argv) > 1 and sys.argv[1] == Config.TEST_FLAG else DevelopmentConfig)


def run_app() -> None:
    cfg: Type[Config] = get_cfg()
    get_app().run(host=cfg.HOST_IP, port=cfg.CORPUS_STORAGE_MANAGER_PORT, use_reloader=False)


if __name__ == "__main__":
    # reloader has to be disabled because of a bug with Flask and multiprocessing
    run_app()
