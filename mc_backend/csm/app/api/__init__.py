"""The API blueprint. Register it on the main application to enable the REST API for text retrieval."""
from flask import Blueprint
from flask_restful import Api

from mcserver import Config

bp = Blueprint("api", __name__)
api = Api(bp)

from . import frequencyAPI
from csm.app.api.annisFindAPI import AnnisFindAPI
from csm.app.api.corpusStorageManagerAPI import CorpusStorageManagerAPI
from csm.app.api.subgraphAPI import SubgraphAPI
from csm.app.api.textcomplexityAPI import TextComplexityAPI

api.add_resource(AnnisFindAPI, Config.SERVER_URI_ANNIS_FIND, endpoint="find")
api.add_resource(CorpusStorageManagerAPI, Config.SERVER_URI_CSM, endpoint="csm")
api.add_resource(SubgraphAPI, Config.SERVER_URI_CSM_SUBGRAPH, endpoint="subgraph")
api.add_resource(TextComplexityAPI, Config.SERVER_URI_TEXT_COMPLEXITY, endpoint='textcomplexity')
