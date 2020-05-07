import rapidjson as json

import flask
from flask_restful import Resource
from flask_restful.reqparse import RequestParser

from mcserver.app.models import AnnisResponse, GraphData, TextComplexity
from mcserver.app.services import NetworkService, CorpusService, TextComplexityService


class TextComplexityAPI(Resource):
    """The Text Complexity API resource. It gives users measures for text complexity for a given text."""

    def __init__(self):
        self.reqparse: RequestParser = NetworkService.base_request_parser.copy()
        self.reqparse.add_argument('urn', type=str, location="data", required=True, help='No URN provided')
        self.reqparse.add_argument('measure', type=str, location="data", required=True, help='No MEASURE provided')
        self.reqparse.add_argument('annis_response', type=dict, location="data", required=False,
                                   help='No ANNIS response provided')
        super(TextComplexityAPI, self).__init__()

    def post(self):
        args: dict = json.loads(flask.request.data.decode("utf-8"))
        urn: str = args["urn"]
        measure: str = args["measure"]
        ar_dict: dict = args.get("annis_response", None)
        ar: AnnisResponse = AnnisResponse(json_dict=ar_dict) if ar_dict else CorpusService.get_corpus(urn, is_csm=True)
        gd: GraphData = GraphData(json_dict=ar.__dict__)
        tc: TextComplexity = TextComplexityService.text_complexity(measure, urn, True, gd)
        return NetworkService.make_json_response(tc.__dict__)
