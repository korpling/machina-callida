from mcserver import get_app, get_cfg

get_app().run(host=get_cfg().HOST_IP_MCSERVER, port=get_cfg().HOST_PORT, use_reloader=False)
