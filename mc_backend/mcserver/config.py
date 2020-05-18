"""Application configuration classes for different environments / use cases"""
import os

from dotenv import load_dotenv
from graphannis.cs import CorpusStorageManager

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config(object):
    """Base configuration for this application.

    Contains information about the current environment,
    different levels of logging, the database, and hosting options.
    The values are shared with all subclasses (if not overridden)."""
    # these have to be at the top
    CURRENT_WORKING_DIRECTORY = os.getcwd()
    CURRENT_WORKING_DIRECTORY_PARENT = os.path.dirname(CURRENT_WORKING_DIRECTORY)
    CURRENT_WORKING_DIRECTORY_PARTS = os.path.split(CURRENT_WORKING_DIRECTORY)  # [::-1]
    GRAPH_DATABASE_DIR = os.path.join(os.sep, "tmp", "graphannis-data")
    MC_SERVER_DIRECTORY = CURRENT_WORKING_DIRECTORY if \
        os.path.split(CURRENT_WORKING_DIRECTORY)[-1] == "mcserver" else os.path.join(CURRENT_WORKING_DIRECTORY,
                                                                                     "mcserver")
    SERVER_URI_BASE = "/mc/api/v1.0/"
    # dirty hack to get the app working either with the Gunicorn/Flask CLI or the PyCharm debugger
    MC_SERVER_APP_DIRECTORY = os.path.join(MC_SERVER_DIRECTORY, "app") if os.path.split(MC_SERVER_DIRECTORY)[
                                                                              -1] == "mcserver" else MC_SERVER_DIRECTORY
    IS_DOCKER = os.environ.get("IS_THIS_A_DOCKER_CONTAINER", False)
    ASSETS_DIRECTORY = os.path.join(MC_SERVER_APP_DIRECTORY, "assets")
    FILES_DIRECTORY = os.path.join(MC_SERVER_APP_DIRECTORY, "files")
    TMP_DIRECTORY = os.path.join(FILES_DIRECTORY, "tmp")
    TREEBANKS_PATH = os.path.join(ASSETS_DIRECTORY, "treebanks")
    TREEBANKS_PROIEL_PATH = os.path.join(TREEBANKS_PATH, "proiel")

    API_SPEC_FILE_PATH = os.path.join(MC_SERVER_DIRECTORY, "mcserver_api.yaml")
    AQL_CASE = "/.*Case=.*/"
    AQL_DEP = "->dep"
    AQL_DEPREL = "deprel"
    AQL_TOK = "tok"
    CACHE_DIRECTORY = os.path.join(MC_SERVER_APP_DIRECTORY, "cache")
    CONLLU2SVG_PATH_LINUX = os.path.join(ASSETS_DIRECTORY, "conllu2svg_linux64")
    CONLLU2SVG_PATH_OSX = os.path.join(ASSETS_DIRECTORY, "conllu2svg_osx")
    CORPUS_STORAGE_MANAGER: CorpusStorageManager = None
    CORPUS_STORAGE_MANAGER_PORT = 6555
    COVERAGE_CONFIGURATION_FILE_NAME = ".coveragerc"
    COVERAGE_ENVIRONMENT_VARIABLE = "COVERAGE_PROCESS_START"
    CSM_DIRECTORY = os.path.join(CURRENT_WORKING_DIRECTORY, "csm")
    CSRF_ENABLED = True
    CTS_API_BASE_URL = "https://cts.perseids.org/api/cts/"
    CUSTOM_CORPUS_CAES_GAL_FILE_PATH = os.path.join(TREEBANKS_PROIEL_PATH, "caes-gal.conllu")
    CUSTOM_CORPUS_CIC_ATT_FILE_PATH = os.path.join(TREEBANKS_PROIEL_PATH, "cic-att.conllu")
    CUSTOM_CORPUS_CIC_OFF_FILE_PATH = os.path.join(TREEBANKS_PROIEL_PATH, "cic-off.conllu")
    CUSTOM_CORPUS_LATIN_NT_FILE_PATH = os.path.join(TREEBANKS_PROIEL_PATH, "latin-nt.conllu")
    CUSTOM_CORPUS_PAL_AGR_FILE_PATH = os.path.join(TREEBANKS_PROIEL_PATH, "pal-agr.conllu")
    CUSTOM_CORPUS_PER_AET_FILE_PATH = os.path.join(TREEBANKS_PROIEL_PATH, "per-aeth.conllu")
    CUSTOM_CORPUS_VIVA_FILE_PATH = os.path.join(ASSETS_DIRECTORY, "viva_lektionstexte1-32.txt")
    CUSTOM_CORPUS_VIVA_URN = "urn:custom:latinLit:viva.lat"
    CUSTOM_CORPUS_PROIEL_URN_TEMPLATE = "urn:custom:latinLit:proiel.{0}.lat"
    DATABASE_TABLE_ALEMBIC = "alembic_version"
    DATABASE_URL_DOCKER = "postgresql://postgres@db:5432/"
    DATABASE_URL_LOCAL = "postgresql://postgres@0.0.0.0:5432/postgres"
    DATABASE_URL_SQLITE = f"sqlite:///{os.path.join(basedir, 'app.db')}"
    DATABASE_URL_SQLITE_MEMORY = "sqlite:///:memory:"
    DATABASE_URL_FALLBACK = DATABASE_URL_DOCKER if IS_DOCKER else DATABASE_URL_SQLITE
    DATABASE_URL = os.environ.get("DATABASE_URL", DATABASE_URL_FALLBACK)
    DEBUG = False
    DOCKER_SERVICE_NAME_CSM = "csm"
    DOCKER_SERVICE_NAME_MCSERVER = "mcserver"
    ERROR_MESSAGE_CORPUS_NOT_FOUND = "A corpus with the specified ID was not found!"
    ERROR_MESSAGE_EXERCISE_NOT_FOUND = "An exercise with the specified ID was not found!"
    ERROR_MESSAGE_INTERNAL_SERVER_ERROR = "The server encountered an unexpected condition that prevented it from " \
                                          "fulfilling the request."
    ERROR_TITLE_INTERNAL_SERVER_ERROR = "Internal Server Error"
    ERROR_TITLE_NOT_FOUND = "Not found"
    FAVICON_FILE_NAME = "favicon.ico"
    FLASK_MIGRATE = "migrate"
    GRAPHANNIS_DEPENDENCY_LINK = "dep"
    GRAPHANNIS_LOG_PATH = os.path.join(os.getcwd(), "graphannis.log")
    H5P_DRAG_TEXT = "drag_text"
    H5P_FILL_BLANKS = "fill_blanks"
    H5P_MULTI_CHOICE = "multi_choice"
    H5P_VOC_LIST = "voc_list"
    # Windows: use 127.0.0.1 as host IP fallback
    HOST_IP_FALLBACK = "0.0.0.0"
    HOST_IP_CSM = DOCKER_SERVICE_NAME_CSM if IS_DOCKER else HOST_IP_FALLBACK
    HOST_IP_MCSERVER = DOCKER_SERVICE_NAME_MCSERVER if IS_DOCKER else HOST_IP_FALLBACK
    HOST_PORT = 5000
    INTERNET_PROTOCOL = "http://"
    INTERVAL_CORPUS_AGE_CHECK = 60 * 60
    INTERVAL_CORPUS_UPDATE = 60 * 60 * 24
    INTERVAL_EXERCISE_DELETE = 60 * 60 * 24 * 30 * 12
    INTERVAL_FILE_DELETE = 60 * 60 * 24
    INTERVAL_STATIC_EXERCISES = 60 * 60 * 24
    IS_PRODUCTION = os.environ.get("FLASK_ENV_VARIABLE", "development") == "production"
    LEARNING_ANALYTICS_DIRECTORY = os.path.join(FILES_DIRECTORY, "learning_analytics")
    LOG_PATH_CSM = f"{DOCKER_SERVICE_NAME_CSM}.log"
    LOG_PATH_MCSERVER = f"{DOCKER_SERVICE_NAME_MCSERVER}.log"
    MIGRATIONS_DIRECTORY = os.path.join(MC_SERVER_DIRECTORY, "migrations")
    NETWORK_GRAPH_TMP_PATH = os.path.join(TMP_DIRECTORY, "graph.svg")
    PANEGYRICI_LATINI_DIRECTORY = os.path.join(ASSETS_DIRECTORY, "panegyrici_latini")
    PANEGYRICI_LATINI_MODEL_PATH = os.path.join(PANEGYRICI_LATINI_DIRECTORY, "panegyrici_latini.model")
    PANEGYRICI_LATINI_TEXT_PATH = os.path.join(PANEGYRICI_LATINI_DIRECTORY, "panegyrici_latini_tokenized.txt")
    PLATFORM_MACOS = "darwin"
    PLATFORM_WINDOWS = "win32"
    PUBLIC_FRONTEND_URL = os.environ.get("PUBLIC_FRONTEND_URL", "http://localhost:8100/")
    REFF_CACHE_DIRECTORY = os.path.join(CACHE_DIRECTORY, "reff")
    SECRET_KEY = 'this-really-needs-to-be-changed'
    # BEGIN endpoints
    # use these endpoints to access the REST API by appending them to the host name (e.g. "http://127.0.0.1:5000")
    SERVER_URI_ANNIS_FIND = SERVER_URI_BASE + "find"
    SERVER_URI_CORPORA = SERVER_URI_BASE + "corpora"
    SERVER_URI_CSM = "/"
    SERVER_URI_CSM_SUBGRAPH = SERVER_URI_CSM + "subgraph"
    SERVER_URI_EXERCISE = SERVER_URI_BASE + "exercise"
    SERVER_URI_EXERCISE_LIST = SERVER_URI_BASE + "exerciseList"
    SERVER_URI_FAVICON = "/favicon.ico"
    SERVER_URI_FILE = SERVER_URI_BASE + "file"
    SERVER_URI_FREQUENCY = SERVER_URI_BASE + "frequency"
    SERVER_URI_H5P = SERVER_URI_BASE + "h5p"
    SERVER_URI_KWIC = SERVER_URI_BASE + "kwic"
    SERVER_URI_RAW_TEXT = SERVER_URI_BASE + "rawtext"
    SERVER_URI_STATIC_EXERCISES = SERVER_URI_BASE + "exercises"
    SERVER_URI_TEXT_COMPLEXITY = SERVER_URI_BASE + "textcomplexity"
    SERVER_URI_VALID_REFF = SERVER_URI_BASE + "validReff"
    SERVER_URI_VECTOR_NETWORK = SERVER_URI_BASE + "vectorNetwork"
    SERVER_URI_VOCABULARY = SERVER_URI_BASE + "vocabulary"
    # END endpoints
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or DATABASE_URL_SQLITE
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STATIC_EXERCISES_REPOSITORY_URL = "https://scm.cms.hu-berlin.de/callidus/machina-callida/-/archive/master/machina-callida-master.zip?path=mc_frontend%2Fsrc%2Fassets%2Fh5p"
    STOP_WORDS_LATIN_PATH = os.path.join(CACHE_DIRECTORY, "stop_words_latin.json")
    STOP_WORDS_URL = "https://raw.githubusercontent.com/aurelberra/stopwords/master/stopwords_latin.json"
    TEST_FLAG = "-test"
    TESTING = False
    TRAP_HTTP_EXCEPTIONS = True
    TREEBANKS_CACHE_DIRECTORY = os.path.join(CACHE_DIRECTORY, "treebanks")
    UDPIPE_MODEL_PATH = os.path.join(ASSETS_DIRECTORY, "latin-ittb-ud-2.0-conll17-170315.udpipe")
    UDPIPE_PATH_LINUX = os.path.join(ASSETS_DIRECTORY, "udpipe_linux64")
    UDPIPE_PATH_OSX = os.path.join(ASSETS_DIRECTORY, "udpipe_osx")
    UDPIPE_PATH_WIN64 = os.path.join(ASSETS_DIRECTORY, "udpipe_win64.exe")
    VOCABULARY_AGLDT_FILE_NAME = "vocabulary_ancient_greek_latin_dependency_treebank.json"
    VOCABULARY_BWS_FILE_NAME = "vocabulary_bamberg_core.json"
    VOCABULARY_PROIEL_FILE_NAME = "vocabulary_proiel_treebank.json"
    VOCABULARY_VIVA_FILE_NAME = "vocabulary_viva.json"


class ProductionConfig(Config):
    """Configuration for the production environment"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL_PROD", Config.DATABASE_URL_FALLBACK)


class StagingConfig(Config):
    """Configuration for staging"""
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    """Configuration for the development environment"""
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = Config.DATABASE_URL_DOCKER if Config.IS_DOCKER else \
        os.environ.get("DATABASE_URL", Config.DATABASE_URL_FALLBACK)


class TestingConfig(Config):
    """Configuration for testing"""
    CTS_API_GET_PASSAGE_URL = "https://cts.perseids.org/api/cts/?request=GetPassage&urn=urn:cts:latinLit:phi1351.phi002.perseus-lat1:2.2"
    HOST_IP_MCSERVER = "0.0.0.0"
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SERVER_NAME = Config.HOST_IP_MCSERVER + ":{0}".format(Config.HOST_PORT)
    SESSION_COOKIE_DOMAIN = False
    SIMULATE_CORPUS_NOT_FOUND = False
    SIMULATE_EMPTY_GRAPH = False
    SIMULATE_HTTP_ERROR = False
    SQLALCHEMY_DATABASE_URI = Config.DATABASE_URL_SQLITE
    STATIC_EXERCISES_ZIP_FILE_PATH = os.path.join(Config.TMP_DIRECTORY, "static_exercises.zip")
    TESTING = True


if __name__ == "__main__":
    a = 0
    # TODO: Write config tests
