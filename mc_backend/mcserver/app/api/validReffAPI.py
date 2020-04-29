from typing import List
from flask_restful import Resource, reqparse, abort
from mcserver.app.services import CorpusService, NetworkService, CustomCorpusService


class ValidReffAPI(Resource):
    """The valid references API resource. It gives users all the citable text references for a corpus."""

    def __init__(self):
        """Initialize possible arguments for calls to the valid references REST API."""
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("urn", type=str, required=True, default="", help="No URN provided")
        super(ValidReffAPI, self).__init__()

    def get(self):
        """The GET method for the valid references REST API. It provides references for the desired text."""
        args = self.reqparse.parse_args()
        urn: str = args["urn"]
        reff: List[str] = CustomCorpusService.get_custom_corpus_reff(urn) if CustomCorpusService.is_custom_corpus_urn(
            urn) else CorpusService.get_standard_corpus_reff(urn)
        if not reff:
            abort(404)
        return NetworkService.make_json_response(reff)
