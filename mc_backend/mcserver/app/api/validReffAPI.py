from typing import List, Union
import connexion
from connexion.lifecycle import ConnexionResponse
from flask import Response

from mcserver import Config
from mcserver.app.services import CorpusService, NetworkService, CustomCorpusService


def get(urn: str) -> Union[Response, ConnexionResponse]:
    """The GET method for the valid references REST API. It provides references for the desired text."""
    reff: List[str] = CustomCorpusService.get_custom_corpus_reff(urn) if CustomCorpusService.is_custom_corpus_urn(
        urn) else CorpusService.get_standard_corpus_reff(urn)
    if not reff:
        return connexion.problem(404, Config.ERROR_TITLE_NOT_FOUND, Config.ERROR_MESSAGE_CORPUS_NOT_FOUND)
    return NetworkService.make_json_response(reff)
