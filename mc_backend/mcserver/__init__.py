"""The main application: Machina Callida.

It is a server-side backend for retrieving Latin texts and
generating language exercises for them."""
import sys
from typing import Type

from flask import Flask
from mcserver.config import Config, ProductionConfig, TestingConfig, DevelopmentConfig
from mcserver.app import create_app


def get_app() -> Flask:
    return create_app(get_cfg())


def get_cfg() -> Type[Config]:
    return ProductionConfig if Config.IS_PRODUCTION else (
        TestingConfig if len(sys.argv) > 1 and sys.argv[1] == Config.TEST_FLAG else DevelopmentConfig)


if __name__ == "__main__":
    # reloader has to be disabled because of a bug with Flask and multiprocessing
    get_app().run(host=get_cfg().HOST_IP_MCSERVER, port=get_cfg().HOST_PORT, use_reloader=False)
