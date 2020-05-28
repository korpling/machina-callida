from typing import Union

import connexion
from connexion.lifecycle import ConnexionResponse
from flask import Response

from mcserver import Config
from mcserver.app.models import AnnisResponse, TextComplexityMeasure
from mcserver.app.services import CorpusService, NetworkService, TextComplexityService


def get(urn: str) -> Union[Response, ConnexionResponse]:
    """Provides the raw text for a requested text passage."""
    ar: AnnisResponse = CorpusService.get_corpus(cts_urn=urn, is_csm=False)
    if not ar.graph_data.nodes:
        return connexion.problem(404, Config.ERROR_TITLE_NOT_FOUND, Config.ERROR_MESSAGE_CORPUS_NOT_FOUND)
    ar.text_complexity = TextComplexityService.text_complexity(TextComplexityMeasure.all.name, urn, False,
                                                               ar.graph_data).to_dict()
    return NetworkService.make_json_response(ar.to_dict())
