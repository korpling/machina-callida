import flask
import requests
from flask_restful import Resource, reqparse
import rapidjson as json

from mcserver import Config
from mcserver.app.services import NetworkService


class FrequencyAPI(Resource):
    def __init__(self):
        # TODO: FIX THE REQUEST PARSING FOR ALL APIs
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("urn", type=str, required=True, default="", location="form", help="No URN provided")
        super(FrequencyAPI, self).__init__()

    def get(self):
        """ Returns results for a frequency query from ANNIS for a given CTS URN and AQL. """
        # get request arguments
        args: dict = flask.request.args
        urn: str = args["urn"]
        url: str = f"{Config.INTERNET_PROTOCOL}{Config.HOST_IP_CSM}:{Config.CORPUS_STORAGE_MANAGER_PORT}" + \
                   Config.SERVER_URI_FREQUENCY
        response: requests.Response = requests.get(url, params=dict(urn=urn))
        return NetworkService.make_json_response(json.loads(response.text))
