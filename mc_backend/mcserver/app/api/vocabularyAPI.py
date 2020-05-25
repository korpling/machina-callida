import string
from typing import Set, List, Dict
from flask_restful import Resource, inputs
from flask_restful.reqparse import RequestParser

from mcserver.app.models import VocabularyCorpus, GraphData, Sentence, AnnisResponse, TextComplexityMeasure
from mcserver.app.services import FileService, CorpusService, AnnotationService, NetworkService, TextService, \
    TextComplexityService


class VocabularyAPI(Resource):
    """ Represents an API for vocabulary comparison.

    It shows whether the vocabulary of a text matches that of another one."""

    def __init__(self):
        self.reqparse: RequestParser = NetworkService.base_request_parser.copy()
        self.reqparse.add_argument("query_urn", type=str, required=True, help="No URN for the query corpus provided")
        self.reqparse.add_argument("vocabulary", type=str, required=True, help="No reference vocabulary provided")
        self.reqparse.add_argument("frequency_upper_bound", type=int, required=True,
                                   help="No upper bound for reference vocabulary frequency provided")
        self.reqparse.add_argument("show_oov", type=str, required=False)
        super(VocabularyAPI, self).__init__()

    def get(self):
        """ Retrieves sentence ID and matching degree for each sentence in the query text. """
        args: dict = self.reqparse.parse_args()
        urn: str = args["query_urn"]
        show_oov: bool = inputs.boolean(args["show_oov"])
        vc: VocabularyCorpus = VocabularyCorpus[args["vocabulary"]]
        vocabulary_set: Set[str] = FileService.get_vocabulary_set(vc, args["frequency_upper_bound"])
        # punctuation should count as a match because we don't want to count this as part of the vocabulary
        for char in string.punctuation:
            vocabulary_set.add(char)
        ar: AnnisResponse = CorpusService.get_corpus(cts_urn=urn, is_csm=False)
        if show_oov:
            # this is not a request for sentence ranges, so we can take a shortcut
            for node in ar.graph_data.nodes:
                if not is_match(target_lemma=node.udep_lemma, vocabulary_set=vocabulary_set):
                    node.is_oov = True
            ar: AnnisResponse = AnnisResponse(
                solutions=[], uri="", exercise_id="", graph_data=ar.graph_data)
            ar.text_complexity = TextComplexityService.text_complexity(TextComplexityMeasure.all.name, urn, False,
                                                                       ar.graph_data).to_dict()
            return NetworkService.make_json_response(ar.to_dict())
        sentences: List[Sentence] = check_vocabulary(ar.graph_data, vocabulary_set)
        return NetworkService.make_json_response([x.__dict__ for x in sentences])


def add_sentence(current_lemmata: Dict[int, str], vocabulary_set: Set[str], sentences: List[Sentence],
                 current_sentence_id: int):
    """ Adds a sentence to the response for the vocabulary check. """
    matches: List[str] = [current_lemmata[i] for i in current_lemmata if is_match(current_lemmata[i], vocabulary_set)]
    new_sentence_matching_degree: int = (len(matches) / len(current_lemmata) * 100) if len(current_lemmata) > 0 else 0
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
