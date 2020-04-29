from datetime import datetime
from typing import Dict

import rapidjson

from flask import Response

from mcserver.app.models import StaticExercise


class NetworkService:
    exercises: Dict[str, StaticExercise] = {}
    exercises_last_update: datetime = datetime.fromtimestamp(0)

    @staticmethod
    def make_json_response(response_input: object):
        """Transforms the resulting objects to JSON so we can send them to the client."""
        dump_result = rapidjson.dumps(response_input)
        response: Response = Response(dump_result, mimetype="application/json")
        # prevent CORS (double check in addition to using the Flask-CORS module)
        response.headers.add('Access-Control-Allow-Origin', '*')
        # prevent CORB
        response.headers.add('Access-Control-Allow-Headers', "Content-Type")
        return response
