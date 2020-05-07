from flask import Flask
from mcserver import get_app, get_cfg

app: Flask = get_app()

if __name__ == "__main__":
    app.run(host=get_cfg().HOST_IP_MCSERVER, port=get_cfg().HOST_PORT, use_reloader=False)
