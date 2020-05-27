from typing import List, Dict, Set
from mcserver.app.models import Phenomenon, FrequencyItem
from mcserver.app.services import NetworkService, CorpusService, AnnotationService


def get(urn: str):
    """ Returns results for a frequency query from ANNIS for a given CTS URN and AQL. """
    fa: List[FrequencyItem] = CorpusService.get_frequency_analysis(urn, is_csm=True)
    # map the abbreviated values found by ANNIS to our own model
    skip_set: Set[Phenomenon] = {Phenomenon.LEMMA, Phenomenon.DEPENDENCY}
    for fi in fa:
        for i in range(len(fi.values)):
            if fi.phenomena[i] in skip_set:
                continue
            value_map: Dict[str, List[str]] = AnnotationService.phenomenon_map[fi.phenomena[i]]
            fi.values[i] = next((x for x in value_map if fi.values[i] in value_map[x]), None)
    return NetworkService.make_json_response([x.to_dict() for x in fa])
