"""The corpus list API. Add it to your REST API to provide users with a list of metadata for available texts."""
from datetime import datetime
from typing import List, Set

import conllu
from conllu import TokenList
from flask_restful import Resource
from flask_restful.reqparse import RequestParser

from mcserver.app import db
from mcserver.app.models import Language, VocabularyCorpus, ResourceType
from mcserver.app.services import NetworkService, FileService
from mcserver.models_auto import Exercise, UpdateInfo


class ExerciseListAPI(Resource):
    """The exercise list API resource. It enables some of the CRUD operations for the exercises from the database."""

    def __init__(self):
        """Initialize possible arguments for calls to the exercise list REST API."""
        self.reqparse: RequestParser = NetworkService.base_request_parser.copy()
        self.reqparse.add_argument("lang", type=str, required=True, help="No language specified")
        self.reqparse.add_argument("last_update_time", type=int, required=False, default=0,
                                   help="No milliseconds time for last update provided")
        self.reqparse.add_argument("vocabulary", type=str, required=False, help="No reference vocabulary provided")
        self.reqparse.add_argument("frequency_upper_bound", type=int, required=False,
                                   help="No upper bound for reference vocabulary frequency provided")
        super(ExerciseListAPI, self).__init__()

    def get(self):
        """The GET method for the exercise list REST API. It provides metadata for all available exercises."""
        args: dict = self.reqparse.parse_args()
        vocabulary_set: Set[str]
        last_update: int = args["last_update_time"]
        ui_exercises: UpdateInfo = db.session.query(UpdateInfo).filter_by(
            resource_type=ResourceType.exercise_list.name).first()
        db.session.commit()
        if ui_exercises.last_modified_time < last_update / 1000:
            return NetworkService.make_json_response([])
        try:
            vc: VocabularyCorpus = VocabularyCorpus[args["vocabulary"]]
            vocabulary_set = FileService.get_vocabulary_set(vc, args["frequency_upper_bound"])
        except KeyError:
            vocabulary_set = set()
        lang: Language
        try:
            lang = Language(args["lang"])
        except ValueError:
            lang = Language.English
        exercises: List[Exercise] = db.session.query(Exercise).filter_by(language=lang.value)
        db.session.commit()
        ret_val: List[dict] = [NetworkService.serialize_exercise(x, compress=True) for x in exercises]
        matching_degrees: List[float] = []
        if len(vocabulary_set):
            for exercise in exercises:
                conll: List[TokenList] = conllu.parse(exercise.conll)
                lemmata: List[str] = [tok["lemma"] for sent in conll for tok in sent.tokens]
                matching_degrees.append(sum((1 if x in vocabulary_set else 0) for x in lemmata) / len(lemmata) * 100)
            for i in range(len(ret_val)):
                ret_val[i]["matching_degree"] = matching_degrees[i]
        return NetworkService.make_json_response(ret_val)
