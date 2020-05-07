import flask
from flask_restful import Resource
from flask_restful.reqparse import RequestParser

from mcserver.app.services import NetworkService, CorpusService


class AnnisFindAPI(Resource):
    def __init__(self):
        self.reqparse: RequestParser = NetworkService.base_request_parser.copy()
        self.reqparse.add_argument("aql", type=str, required=True, location="form", help="No AQL provided")
        self.reqparse.add_argument("urn", type=str, required=True, default="", location="form", help="No URN provided")
        super(AnnisFindAPI, self).__init__()

    def get(self):
        """ Returns matches from ANNIS for a given CTS URN and AQL. """
        # get request arguments
        args: dict = flask.request.args
        urn: str = args["urn"]
        aql: str = args["aql"]
        return NetworkService.make_json_response(CorpusService.find_matches(urn, aql, is_csm=True))
