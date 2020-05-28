from mcserver.app.models import AnnisResponse, TextComplexity
from mcserver.app.services import NetworkService, CorpusService, TextComplexityService


def get(measure: str, urn: str):
    """Gives users measures of text complexity for a given text."""
    ar: AnnisResponse = CorpusService.get_corpus(urn, is_csm=False)
    tc: TextComplexity = TextComplexityService.text_complexity(measure, urn, False, ar.graph_data)
    return NetworkService.make_json_response(tc.to_dict())
