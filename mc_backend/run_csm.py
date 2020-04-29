from flask import Flask

from csm import get_app, get_cfg

app: Flask = get_app()

if __name__ == "__main__":
    app.run(host=get_cfg().HOST_IP, port=get_cfg().CORPUS_STORAGE_MANAGER_PORT, use_reloader=False)
