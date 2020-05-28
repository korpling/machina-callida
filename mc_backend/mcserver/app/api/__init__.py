"""The API blueprint. Register it on the main application to enable the REST API for text retrieval."""
from flask import Blueprint
from flask_restful import Api

bp = Blueprint("api", __name__)
api = Api(bp)

from . import corpusAPI, corpusListAPI, exerciseAPI, exerciseListAPI, fileAPI, frequencyAPI, h5pAPI, kwicAPI, \
    rawTextAPI, staticExercisesAPI, textcomplexityAPI, validReffAPI, vectorNetworkAPI, vocabularyAPI
