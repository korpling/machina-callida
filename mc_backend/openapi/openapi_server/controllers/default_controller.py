import connexion
import six

from openapi.openapi_server.models.annis_response import AnnisResponse  # noqa: E501
from openapi.openapi_server.models.corpus import Corpus  # noqa: E501
from openapi.openapi_server.models.file_type import FileType  # noqa: E501
from openapi.openapi_server.models.frequency_item import FrequencyItem  # noqa: E501
from openapi.openapi_server.models.matching_exercise import MatchingExercise  # noqa: E501
from openapi.openapi_server.models.sentence import Sentence  # noqa: E501
from openapi.openapi_server.models.static_exercise import StaticExercise  # noqa: E501
from openapi.openapi_server.models.text_complexity import TextComplexity  # noqa: E501
from openapi.openapi_server.models.vocabulary_mc import VocabularyMC  # noqa: E501
from openapi.openapi_server import util


def mcserver_app_api_corpus_api_delete(cid):  # noqa: E501
    """Deletes a single corpus by ID.

     # noqa: E501

    :param cid: Corpus identifier.
    :type cid: int

    :rtype: bool
    """
    return 'do some magic!'


def mcserver_app_api_corpus_api_get(cid):  # noqa: E501
    """Returns a single corpus by ID.

     # noqa: E501

    :param cid: Corpus identifier.
    :type cid: int

    :rtype: Corpus
    """
    return 'do some magic!'


def mcserver_app_api_corpus_api_patch(cid, author=None, source_urn=None, title=None):  # noqa: E501
    """Updates a single corpus by ID.

     # noqa: E501

    :param cid: Corpus identifier.
    :type cid: int
    :param author: Author of the texts in the corpus.
    :type author: str
    :param source_urn: CTS base URN for referencing the corpus.
    :type source_urn: str
    :param title: Corpus title.
    :type title: str

    :rtype: Corpus
    """
    return 'do some magic!'


def mcserver_app_api_corpus_list_api_get(last_update_time):  # noqa: E501
    """Returns a list of corpora.

     # noqa: E501

    :param last_update_time: Time (in milliseconds) of the last update.
    :type last_update_time: int

    :rtype: Corpus
    """
    return 'do some magic!'


def mcserver_app_api_exercise_api_get(eid):  # noqa: E501
    """Returns exercise data by ID.

     # noqa: E501

    :param eid: Unique identifier (UUID) for the exercise.
    :type eid: str

    :rtype: AnnisResponse
    """
    return 'do some magic!'


def mcserver_app_api_exercise_api_post():  # noqa: E501
    """Creates a new exercise.

     # noqa: E501


    :rtype: AnnisResponse
    """
    return 'do some magic!'


def mcserver_app_api_exercise_list_api_get(lang, frequency_upper_bound=None, last_update_time=None, vocabulary=None):  # noqa: E501
    """Provides metadata for all available exercises.

     # noqa: E501

    :param lang: ISO 639-1 Language Code for the localization of exercise content.
    :type lang: str
    :param frequency_upper_bound: Upper bound for reference vocabulary frequency.
    :type frequency_upper_bound: int
    :param last_update_time: Time (in milliseconds) of the last update.
    :type last_update_time: int
    :param vocabulary: Identifier for a reference vocabulary.
    :type vocabulary: dict | bytes

    :rtype: List[MatchingExercise]
    """
    if connexion.request.is_json:
        vocabulary =  VocabularyMC.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def mcserver_app_api_file_api_get(id, type, solution_indices=None):  # noqa: E501
    """Provides the URL to download a specific file.

     # noqa: E501

    :param id: Unique identifier (UUID) for an exercise.
    :type id: str
    :param type: File format for the requested download.
    :type type: dict | bytes
    :param solution_indices: Indices for the solutions that should be included in the download.
    :type solution_indices: List[int]

    :rtype: object
    """
    if connexion.request.is_json:
        type =  FileType.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def mcserver_app_api_file_api_post(file_type=None, html_content=None, learning_result=None, urn=None):  # noqa: E501
    """Serializes and persists learning results or HTML content for later access.

     # noqa: E501

    :param file_type: 
    :type file_type: dict | bytes
    :param html_content: HTML content to be serialized.
    :type html_content: str
    :param learning_result: Serialized XAPI results for an interactive exercise.
    :type learning_result: str
    :param urn: CTS URN for the text passage from which the HTML content was created.
    :type urn: str

    :rtype: str
    """
    if connexion.request.is_json:
        file_type = FileType.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def mcserver_app_api_frequency_api_get(urn):  # noqa: E501
    """Returns results for a frequency query from ANNIS for a given CTS URN.

     # noqa: E501

    :param urn: CTS URN for referencing the corpus.
    :type urn: str

    :rtype: List[FrequencyItem]
    """
    return 'do some magic!'


def mcserver_app_api_h5p_api_get(eid, lang, solution_indices=None):  # noqa: E501
    """Provides JSON templates for client-side H5P exercise layouts.

     # noqa: E501

    :param eid: Unique identifier (UUID) for the exercise.
    :type eid: str
    :param lang: ISO 639-1 Language Code for the localization of exercise content.
    :type lang: str
    :param solution_indices: Indices for the solutions that should be included in the download.
    :type solution_indices: List[int]

    :rtype: object
    """
    return 'do some magic!'


def mcserver_app_api_kwic_api_post(search_values, urn, ctx_left, ctx_right):  # noqa: E501
    """Provides example contexts for a given phenomenon in a given corpus.

     # noqa: E501

    :param search_values: Search queries that were used to build the exercise.
    :type search_values: str
    :param urn: CTS URN for the text passage from which the KWIC view should be generated.
    :type urn: str
    :param ctx_left: Number of tokens that should be given as context on the left side of a target.
    :type ctx_left: int
    :param ctx_right: Number of tokens that should be given as context on the right side of a target.
    :type ctx_right: int

    :rtype: str
    """
    return 'do some magic!'


def mcserver_app_api_raw_text_api_get(urn):  # noqa: E501
    """Provides the raw text for a requested text passage.

     # noqa: E501

    :param urn: CTS URN for referencing the corpus.
    :type urn: str

    :rtype: AnnisResponse
    """
    return 'do some magic!'


def mcserver_app_api_static_exercises_api_get():  # noqa: E501
    """Returns metadata for static exercises.

     # noqa: E501


    :rtype: Dict[str, StaticExercise]
    """
    return 'do some magic!'


def mcserver_app_api_textcomplexity_api_get(measure, urn):  # noqa: E501
    """Gives users measures of text complexity for a given text.

     # noqa: E501

    :param measure: The desired measure of text complexity for the given text passage.
    :type measure: str
    :param urn: CTS URN for referencing the corpus.
    :type urn: str

    :rtype: TextComplexity
    """
    return 'do some magic!'


def mcserver_app_api_valid_reff_api_get(urn):  # noqa: E501
    """Gives users all the citable text references for a corpus.

     # noqa: E501

    :param urn: CTS URN for referencing the corpus.
    :type urn: str

    :rtype: List[str]
    """
    return 'do some magic!'


def mcserver_app_api_vector_network_api_get(search_regex, highlight_regex=None, min_count=None, nearest_neighbor_count=None):  # noqa: E501
    """Provides network data for the vectors in an AI model.

     # noqa: E501

    :param search_regex: Regular expression to determine relevant words in the text.
    :type search_regex: str
    :param highlight_regex: Regular expression to determine words in the text that should be highlighted.
    :type highlight_regex: str
    :param min_count: Minimum number of occurrences that a word needs to be included in the analysis.
    :type min_count: int
    :param nearest_neighbor_count: Number of nearest neighbors that should be considered for each relevant word.
    :type nearest_neighbor_count: int

    :rtype: str
    """
    return 'do some magic!'


def mcserver_app_api_vector_network_api_post(search_regex, nearest_neighbor_count=None):  # noqa: E501
    """Provides network data for the vectors in an AI model.

     # noqa: E501

    :param search_regex: Regular expression for a textual search.
    :type search_regex: str
    :param nearest_neighbor_count: Number of nearest neighbors that should be considered for each target node in a graph analysis.
    :type nearest_neighbor_count: int

    :rtype: List[List[str]]
    """
    return 'do some magic!'


def mcserver_app_api_vocabulary_api_get(frequency_upper_bound, query_urn, vocabulary):  # noqa: E501
    """Shows how well the vocabulary of a text matches a predefined reference vocabulary.

     # noqa: E501

    :param frequency_upper_bound: Upper bound for reference vocabulary frequency.
    :type frequency_upper_bound: int
    :param query_urn: URN for the query corpus.
    :type query_urn: str
    :param vocabulary: Identifier for a reference vocabulary.
    :type vocabulary: dict | bytes

    :rtype: List[Sentence]
    """
    if connexion.request.is_json:
        vocabulary =  VocabularyMC.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def mcserver_app_api_vocabulary_api_post(frequency_upper_bound, query_urn, vocabulary):  # noqa: E501
    """Shows how well the vocabulary of a text matches a predefined reference vocabulary.

     # noqa: E501

    :param frequency_upper_bound: Upper bound for reference vocabulary frequency.
    :type frequency_upper_bound: int
    :param query_urn: URN for the query corpus.
    :type query_urn: str
    :param vocabulary: 
    :type vocabulary: dict | bytes

    :rtype: AnnisResponse
    """
    if connexion.request.is_json:
        vocabulary = VocabularyMC.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
