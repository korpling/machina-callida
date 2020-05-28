from mcserver.app.models import AnnisResponse, TextComplexity
from mcserver.app.services import NetworkService, CorpusService, TextComplexityService
from openapi.openapi_server.models import TextComplexityForm


def post(complexity_data: dict):
    tcf: TextComplexityForm = TextComplexityForm.from_dict(complexity_data)
    ar: AnnisResponse = AnnisResponse.from_dict(
        tcf.annis_response.to_dict()) if tcf.annis_response else CorpusService.get_corpus(tcf.urn, is_csm=True)
    tc: TextComplexity = TextComplexityService.text_complexity(tcf.measure, tcf.urn, True, ar.graph_data)
    return NetworkService.make_json_response(tc.to_dict())
