"""Configuration for the gunicorn server"""
from mcserver import Config

bind = "{0}:{1}".format(Config.HOST_IP, Config.CORPUS_STORAGE_MANAGER_PORT)
debug = False
reload = True
timeout = 3600
workers = 1
