from flask_restful import Resource, abort
from flask_restful.reqparse import RequestParser

from mcserver.app.models import AnnisResponse, TextComplexityMeasure, GraphData
from mcserver.app.services import CorpusService, NetworkService, TextComplexityService


class RawTextAPI(Resource):
    """The fill the blank API resource. It creates a fill the blank exercise for a given text."""

    def __init__(self):
        """Initialize possible arguments for calls to the fill the blank REST API."""
        self.reqparse: RequestParser = NetworkService.base_request_parser.copy()
        self.reqparse.add_argument("urn", type=str, required=True, default="", help="No URN provided")
        super(RawTextAPI, self).__init__()

    def get(self):
        args = self.reqparse.parse_args()
        urn: str = args["urn"]
        ar: AnnisResponse = CorpusService.get_corpus(cts_urn=urn, is_csm=False)
        if not ar.nodes:
            abort(404)
        gd: GraphData = GraphData(json_dict=ar.__dict__)
        ar.text_complexity = TextComplexityService.text_complexity(TextComplexityMeasure.all.name, urn, False, gd)
        return NetworkService.make_json_response(ar.__dict__)
