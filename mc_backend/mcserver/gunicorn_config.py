"""Configuration for the gunicorn server"""
import multiprocessing

from mcserver import Config

bind = "{0}:{1}".format(Config.HOST_IP, Config.HOST_PORT)
debug = False
reload = True
timeout = 3600
workers = multiprocessing.cpu_count() * 2 + 1
