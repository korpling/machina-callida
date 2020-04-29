from csm import get_app, get_cfg

get_app().run(host=get_cfg().HOST_IP, port=get_cfg().HOST_PORT, use_reloader=False)
