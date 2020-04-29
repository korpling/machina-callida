import json
from json import JSONDecodeError
from typing import Dict, List

import flask
from conllu import TokenList
from flask_restful import Resource, reqparse, abort

from mcserver.app.models import ExerciseType, Phenomenon, AnnisResponse
from mcserver.app.services import CorpusService, NetworkService


class CorpusStorageManagerAPI(Resource):
    """Represents an API for the Corpus Storage Manager.

    It manages the database and everything corpus-related."""

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("title", type=str, required=True, location="data", help="No title provided")
        self.reqparse.add_argument("annotations", required=True, location="data",
                                   help="No annotations provided")
        self.reqparse.add_argument("aqls", required=True, location="data", help="No AQLs provided",
                                   action="append")
        self.reqparse.add_argument("exercise_type", type=str, required=True, location="data",
                                   help="No exercise type provided")
        self.reqparse.add_argument("search_phenomena", type=str, required=False, location="data",
                                   help="No search phenomena provided")
        self.reqparse.add_argument("urn", type=str, required=False, help="No text identifier provided")
        super(CorpusStorageManagerAPI, self).__init__()

    def get(self):
        """ Returns graph data for a given CTS URN. """
        # get request arguments
        args: Dict = flask.request.args
        cts_urn: str = args["urn"]
        ar: AnnisResponse = CorpusService.get_corpus(cts_urn=cts_urn, is_csm=True)
        if not ar.nodes:
            abort(404)
        return NetworkService.make_json_response(ar.__dict__)

    def post(self):
        """Given the relevant corpus data, gives back search results as graph data."""
        args: dict = {}
        try:
            args = json.loads(flask.request.data.decode("utf-8"))
        except JSONDecodeError:
            abort(400)
        title: str = args["title"]
        annotations_or_urn: str = args["annotations"]
        aqls: List[str] = args["aqls"]
        exercise_type: ExerciseType = ExerciseType[args["exercise_type"]]
        search_phenomena: List[Phenomenon] = [Phenomenon[x] for x in args["search_phenomena"]]
        conll: List[TokenList] = CorpusService.get_annotations_from_string(annotations_or_urn)
        ret_val: dict = CorpusService.process_corpus_data(title, conll, aqls, exercise_type, search_phenomena)
        # serialize the results to json
        return NetworkService.make_json_response(ret_val)
