import string
from typing import Set, List, Dict

from flask import Response

from mcserver.app.models import VocabularyCorpus, GraphData, Sentence, AnnisResponse, TextComplexityMeasure
from mcserver.app.services import FileService, CorpusService, AnnotationService, NetworkService, TextService, \
    TextComplexityService
from openapi.openapi_server.models import VocabularyForm


def add_sentence(current_lemmata: Dict[int, str], vocabulary_set: Set[str], sentences: List[Sentence],
                 current_sentence_id: int):
    """ Adds a sentence to the response for the vocabulary check. """
    matches: List[str] = [current_lemmata[i] for i in current_lemmata if is_match(current_lemmata[i], vocabulary_set)]
    new_sentence_matching_degree: float = (len(matches) / len(current_lemmata) * 100) if len(current_lemmata) > 0 else 0
    sentences.append(Sentence(id=current_sentence_id, matching_degree=new_sentence_matching_degree))


def check_lemma_suffix(target_lemma: str, vocabulary_set: Set[str]):
    """ Checks whether slightly different forms of the lemma are matched by the vocabulary set. """
    for suffix in TextService.suffix_map:
        if target_lemma[-len(suffix):] == suffix:
            for replacement in TextService.suffix_map[suffix]:
                if (target_lemma[:-len(suffix)] + replacement) in vocabulary_set:
                    return True
    return False


def check_vocabulary(graph_data: GraphData, vocabulary_set: Set[str]) -> List[Sentence]:
    """ Checks whether the lemmata of a given graph/text match a reference vocabulary. """
    sentences: List[Sentence] = []
    current_sentence_id: int = AnnotationService.get_sentence_id(graph_data.nodes[0])
    # mapping from node indices to the respective lemma
    current_lemmata: Dict[int, str] = {}
    for i in range(len(graph_data.nodes)):
        new_sentence_id: int = AnnotationService.get_sentence_id(graph_data.nodes[i])
        if new_sentence_id != current_sentence_id:
            add_sentence(current_lemmata=current_lemmata, vocabulary_set=vocabulary_set, sentences=sentences,
                         current_sentence_id=current_sentence_id)
            current_lemmata = {}
            current_sentence_id = new_sentence_id
        current_lemmata[i] = graph_data.nodes[i].udep_lemma
    # add the last sentence because the sentence ID won't change anymore
    add_sentence(current_lemmata=current_lemmata, vocabulary_set=vocabulary_set, sentences=sentences,
                 current_sentence_id=current_sentence_id)
    return sentences


def get(frequency_upper_bound: int, query_urn: str, vocabulary: str) -> Response:
    """ Retrieves sentence ID and matching degree for each sentence in the query text. """
    vc: VocabularyCorpus = VocabularyCorpus[vocabulary]
    vocabulary_set: Set[str] = FileService.get_vocabulary_set(vc, frequency_upper_bound)
    # punctuation should count as a match because we don't want to count this as part of the vocabulary
    for char in string.punctuation:
        vocabulary_set.add(char)
    ar: AnnisResponse = CorpusService.get_corpus(cts_urn=query_urn, is_csm=False)
    sentences: List[Sentence] = check_vocabulary(ar.graph_data, vocabulary_set)
    return NetworkService.make_json_response([x.to_dict() for x in sentences])


def is_match(target_lemma: str, vocabulary_set: Set[str]):
    """ Checks whether a given lemma is part of a reference vocabulary."""
    if target_lemma in vocabulary_set:
        return True
    elif "#" in target_lemma and target_lemma.split("#")[0] in vocabulary_set:
        return True
    elif check_lemma_suffix(target_lemma, vocabulary_set):
        return True
    elif target_lemma in TextService.proper_nouns_set:
        return True
    # doesn't check for spelling variants (minerua/minerva)
    # maybe perform a second check after the orthography check
    else:
        for key in TextService.orthography_map:
            if key in target_lemma and target_lemma.replace(key, TextService.orthography_map[key]) in vocabulary_set:
                return True
        return False
    # TODO: ADD CASES FOR MISSING ASSIMILATION, E.G. "ADPONERE" INSTEAD OF "APPONERE"


def post(vocabulary_data: dict):
    """ Indicates for each token of a corpus whether it is covered by a reference vocabulary. """
    vf: VocabularyForm = VocabularyForm.from_dict(vocabulary_data)
    vc: VocabularyCorpus = VocabularyCorpus[vf.vocabulary]
    vocabulary_set: Set[str] = FileService.get_vocabulary_set(vc, vf.frequency_upper_bound)
    # punctuation should count as a match because we don't want to count this as part of the vocabulary
    for char in string.punctuation:
        vocabulary_set.add(char)
    ar: AnnisResponse = CorpusService.get_corpus(cts_urn=vf.query_urn, is_csm=False)
    for node in ar.graph_data.nodes:
        if not is_match(target_lemma=node.udep_lemma, vocabulary_set=vocabulary_set):
            node.is_oov = True
    ar: AnnisResponse = AnnisResponse(
        solutions=[], uri="", exercise_id="", graph_data=ar.graph_data)
    ar.text_complexity = TextComplexityService.text_complexity(
        TextComplexityMeasure.all.name, vf.query_urn, False, ar.graph_data).to_dict()
    return NetworkService.make_json_response(ar.to_dict())
