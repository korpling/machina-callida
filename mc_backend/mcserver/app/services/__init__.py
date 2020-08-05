"""Common services shared by the various application components."""

from flask import Blueprint

bp = Blueprint("services", __name__)

# the order of imports is very important, please don't change it if you don't know what you are doing
from mcserver.app.services.databaseService import DatabaseService
from mcserver.app.services.textService import TextService
from mcserver.app.services.xmlService import XMLservice
from mcserver.app.services.fileService import FileService
from mcserver.app.services.networkService import NetworkService
from mcserver.app.services.annotationService import AnnotationService
from mcserver.app.services.customCorpusService import CustomCorpusService
from mcserver.app.services.frequencyService import FrequencyService
from mcserver.app.services.corpusService import CorpusService
from mcserver.app.services.textComplexityService import TextComplexityService
from mcserver.app.services.exerciseService import ExerciseService
