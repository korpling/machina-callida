from flask_restful import Resource
from flask_restful.reqparse import RequestParser

from mcserver.app.models import AnnisResponse, GraphData, TextComplexity
from mcserver.app.services import NetworkService, CorpusService, TextComplexityService


class TextComplexityAPI(Resource):
    """The Text Complexity API resource. It gives users measures for text complexity for a given text."""

    def __init__(self):
        self.reqparse: RequestParser = NetworkService.base_request_parser.copy()
        self.reqparse.add_argument('urn', type=str, required=True, help='No URN provided')
        self.reqparse.add_argument('measure', type=str, required=True, help='No MEASURE provided')
        super(TextComplexityAPI, self).__init__()

    def get(self):
        args: dict = self.reqparse.parse_args()
        urn: str = args["urn"]
        measure: str = args["measure"]
        ar: AnnisResponse = CorpusService.get_corpus(urn, is_csm=False)
        tc: TextComplexity = TextComplexityService.text_complexity(measure, urn, False, ar.graph_data)
        return NetworkService.make_json_response(tc.to_dict())
