from typing import List, Dict, Set
import flask
from flask_restful import Resource
from flask_restful.reqparse import RequestParser

from mcserver.app.models import FrequencyAnalysis, Phenomenon
from mcserver.app.services import NetworkService, CorpusService, AnnotationService


class FrequencyAPI(Resource):
    def __init__(self):
        self.reqparse: RequestParser = NetworkService.base_request_parser.copy()
        self.reqparse.add_argument("urn", type=str, required=True, default="", location="form", help="No URN provided")
        super(FrequencyAPI, self).__init__()

    def get(self):
        """ Returns results for a frequency query from ANNIS for a given CTS URN and AQL. """
        # get request arguments
        args: dict = flask.request.args
        urn: str = args["urn"]
        fa: FrequencyAnalysis = CorpusService.get_frequency_analysis(urn, is_csm=True)
        # map the abbreviated values found by ANNIS to our own model
        skip_set: Set[Phenomenon] = {Phenomenon.lemma, Phenomenon.dependency}
        for fi in fa:
            for i in range(len(fi.values)):
                if fi.phenomena[i] in skip_set:
                    continue
                value_map: Dict[str, List[str]] = AnnotationService.phenomenon_map[fi.phenomena[i]]
                fi.values[i] = next((x for x in value_map if fi.values[i] in value_map[x]), None)
        return NetworkService.make_json_response(fa.serialize())
