import json
from datetime import datetime
from typing import Dict

import rapidjson

from flask import Response
from flask_restful.reqparse import RequestParser

from mcserver import Config
from mcserver.app.models import StaticExercise
from mcserver.models_auto import Exercise, TExercise


class NetworkService:
    base_request_parser: RequestParser = RequestParser(bundle_errors=True)
    exercises: Dict[str, StaticExercise] = {}
    exercises_last_update: datetime = datetime.fromtimestamp(0)

    @staticmethod
    def get_exercise_uri(exercise: Exercise):
        return f"{Config.SERVER_URI_FILE}/{exercise.eid}"

    @staticmethod
    def make_json_response(response_input: object, indent: int = None) -> Response:
        """Transforms the resulting objects to JSON so we can send them to the client."""
        dump_result = rapidjson.dumps(response_input, indent=indent)
        response: Response = Response(dump_result, mimetype="application/json")
        # prevent CORS (double check in addition to using the Flask-CORS module)
        response.headers.add('Access-Control-Allow-Origin', '*')
        # prevent CORB
        response.headers.add('Access-Control-Allow-Headers', "Content-Type")
        return response

    @staticmethod
    def serialize_exercise(exercise: TExercise, compress: bool) -> dict:
        """ Serializes an exercise to JSON format. """
        ret_val: dict = exercise.to_dict()
        ret_val["conll"] = "" if compress else exercise.conll
        # convert the POSIX timestamp to JSON / Javascript, i.e. from seconds to milliseconds
        ret_val["last_access_time"] = exercise.last_access_time * 1000
        ret_val["search_values"] = json.loads(exercise.search_values)
        ret_val["solutions"] = "[]" if compress else json.loads(exercise.solutions)
        return ret_val
