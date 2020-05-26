"""The API blueprint. Register it on the main application to enable the REST API for text retrieval."""
from flask import Blueprint
from flask_restful import Api
from mcserver import Config

bp = Blueprint("api", __name__)
api = Api(bp)

from . import corpusAPI, corpusListAPI, exerciseAPI, staticExercisesAPI
from mcserver.app.api.exerciseListAPI import ExerciseListAPI
from mcserver.app.api.fileAPI import FileAPI
from mcserver.app.api.frequencyAPI import FrequencyAPI
from mcserver.app.api.h5pAPI import H5pAPI
from mcserver.app.api.kwicAPI import KwicAPI
from mcserver.app.api.rawTextAPI import RawTextAPI
from mcserver.app.api.textcomplexityAPI import TextComplexityAPI
from mcserver.app.api.validReffAPI import ValidReffAPI
from mcserver.app.api.vectorNetworkAPI import VectorNetworkAPI
from mcserver.app.api.vocabularyAPI import VocabularyAPI

api.add_resource(ExerciseListAPI, Config.SERVER_URI_EXERCISE_LIST, endpoint="exerciseList")
api.add_resource(FileAPI, Config.SERVER_URI_FILE, endpoint="file")
api.add_resource(FrequencyAPI, Config.SERVER_URI_FREQUENCY, endpoint="frequency")
api.add_resource(H5pAPI, Config.SERVER_URI_H5P, endpoint="h5p")
api.add_resource(KwicAPI, Config.SERVER_URI_KWIC, endpoint="kwic")
api.add_resource(RawTextAPI, Config.SERVER_URI_RAW_TEXT, endpoint="rawtext")
api.add_resource(TextComplexityAPI, Config.SERVER_URI_TEXT_COMPLEXITY, endpoint='textcomplexity')
api.add_resource(ValidReffAPI, Config.SERVER_URI_VALID_REFF, endpoint="validReff")
api.add_resource(VectorNetworkAPI, Config.SERVER_URI_VECTOR_NETWORK, endpoint="vectorNetwork")
api.add_resource(VocabularyAPI, Config.SERVER_URI_VOCABULARY, endpoint="vocabulary")
