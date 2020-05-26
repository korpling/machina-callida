import connexion
import six

from openapi.openapi_server.models.annis_response import AnnisResponse  # noqa: E501
from openapi.openapi_server.models.corpus import Corpus  # noqa: E501
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


def mcserver_app_api_static_exercises_api_get():  # noqa: E501
    """Returns metadata for static exercises.

     # noqa: E501


    :rtype: object
    """
    return 'do some magic!'
