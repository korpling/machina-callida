import json
from typing import Dict, List, Set

import requests
from mcserver import Config
from mcserver.app.models import GraphData, TextComplexity, TextComplexityMeasure, AnnisResponse
from mcserver.app.services import TextService, AnnotationService, CorpusService
from openapi.openapi_server.models import TextComplexityForm


class TextComplexityService:
    """ Service for calculating text complexity. """
    current_graph_data: GraphData

    @staticmethod
    def average_sentence_length(urn: str, is_csm: bool) -> float:
        """ Gives back the average sentence length. """
        words: int = TextComplexityService.how_many_words(urn, is_csm)
        sentences: int = TextComplexityService.how_many_sentences(urn, is_csm)
        return words / sentences

    @staticmethod
    def average_word_length(urn: str, is_csm: bool) -> float:
        """Gives back the mean number of characters for word."""
        tok_lengths: List[int] = [len(x.annis_tok) for x in TextComplexityService.current_graph_data.nodes]
        return sum(tok_lengths) / len(tok_lengths)

    @staticmethod
    def calculate_overall_complexity(tc: TextComplexity) -> float:
        """ Combines all the single elements of text complexity into one measure with a scale from 0 to 100. """
        # the overall scale for all the separate measures should be from 0 to 100
        tc_measure_overall: List[float] = []
        wcrs: List[range] = TextService.word_count_ranges
        # each range/index is separated evenly across the scale
        wcr_idx: int = next(i for i in range(len(wcrs)) if tc.n_w in wcrs[i]) + 1
        tc_measure_overall.append(wcr_idx / len(wcrs) * 100)
        # need to take care of empty text (0 POS); there are 17 different POS tags overall
        tc_measure_overall.append((tc.pos + 1) * (100 / 16))
        scrs: List[range] = TextService.sentence_count_ranges
        # each range/index is separated evenly across the scale
        scr_idx: int = next(i for i in range(len(scrs)) if tc.n_w in scrs[i]) + 1
        tc_measure_overall.append(scr_idx / len(scrs) * 100)
        max_w_per_sent: int = 700
        tc_measure_overall.append(tc.avg_w_per_sent / max_w_per_sent * 100)
        max_w_len: int = 50
        tc_measure_overall.append(tc.avg_w_len / max_w_len * 100)
        # we do not use the punctuation count because it needs to differentiated into various categories, e.g.
        # whether it represents a subclause or an enumeration; we already calculate subclauses separately
        tc_measure_overall.append(tc.n_types / tc.n_w * 100)
        tc_measure_overall.append(tc.lex_den * 100)
        # all the other measures need to be normalized for text length, e.g. word/sentence/clause count
        divisor: int = max(tc.n_clause + tc.n_subclause, 1)
        tc_measure_overall.append((tc.n_subclause / divisor) * 100)
        tc_measure_overall.append((tc.n_abl_abs / divisor) * 100)
        tc_measure_overall.append((tc.n_gerund / divisor) * 100)
        tc_measure_overall.append((tc.n_inf / divisor) * 100)
        tc_measure_overall.append((tc.n_part / divisor) * 100)
        return round(sum(tc_measure_overall) / len(tc_measure_overall), 2)

    @staticmethod
    def get_measure_map() -> Dict[str, callable]:
        """ Maps each measure to its corresponding calculation function. """
        return {
            "n_w": TextComplexityService.how_many_words, "pos": TextComplexityService.how_many_pos,
            "n_sent": TextComplexityService.how_many_sentences,
            "avg_w_per_sent": TextComplexityService.average_sentence_length,
            "avg_w_len": TextComplexityService.average_word_length,
            "n_punct": TextComplexityService.how_many_punctuation,
            "n_types": TextComplexityService.how_many_types, "lex_den": TextComplexityService.lexical_density,
            "n_clause": TextComplexityService.how_many_main_clauses,
            "n_subclause": TextComplexityService.how_many_sub_clauses,
            "n_abl_abs": TextComplexityService.how_many_ablativi_absoluti,
            "n_gerund": TextComplexityService.how_many_gerunds, "n_inf": TextComplexityService.how_many_infinitives,
            "n_part": TextComplexityService.how_many_participles}

    @staticmethod
    def get_types() -> Set[str]:
        """ Gives back the types in the text. """
        return set(x.annis_tok for x in TextComplexityService.current_graph_data.nodes)

    @staticmethod
    def how_many_ablativi_absoluti(urn: str, is_csm: bool) -> int:
        """ Gives back the number of ablativi absoluti in the text. """
        aql: str = "tok ->dep[deprel=/(nsubj|nsubj:pass|csubj|csubj:pass)/] feats=/.*Abl.*/"
        node_ids: List[str] = CorpusService.find_matches(urn, aql, is_csm=is_csm)
        return round(len(node_ids) / 2)

    @staticmethod
    def how_many_gerunds(urn: str, is_csm: bool) -> int:
        """ Gives back the number of gerunds in the text. """
        aql: str = "feats=/.*VerbForm=Ger.*/"
        node_ids: List[str] = CorpusService.find_matches(urn, aql, is_csm=is_csm)
        # TODO: gerundivo
        return len(node_ids)

    @staticmethod
    def how_many_infinitives(urn: str, is_csm: bool) -> int:
        """ Gives back the number of infinitives in the text. """
        aql: str = 'feats=/.*Inf.*/ ->dep[deprel=/(nsubj|nsubj:pass|csubj|csubj:pass)/] feats=/.*Acc.*/'
        node_ids: List[str] = CorpusService.find_matches(urn, aql, is_csm=is_csm)
        aql = 'feats=/.*Acc.*/ ->dep[deprel=/(xcomp|ccomp)/] feats=/.*Inf.*/'
        node_ids += CorpusService.find_matches(urn, aql, is_csm=is_csm)
        return round(len(node_ids) / 2)

    @staticmethod
    def how_many_main_clauses(urn: str, is_csm: bool) -> int:
        """ Gives back how many clauses are in the text. """
        # TODO: ellipsis not counted
        aql: str = "deps"
        node_ids: List[str] = CorpusService.find_matches(urn, aql, is_csm=is_csm)
        return len(node_ids)

    @staticmethod
    def how_many_participles(urn: str, is_csm: bool) -> int:
        """Gives back how many participles are in the text"""
        aql: str = "feats=/.*VerbForm=Part.*/"
        node_ids: List[str] = CorpusService.find_matches(urn, aql, is_csm=is_csm)
        return len(node_ids)

    @staticmethod
    def how_many_pos(urn: str, is_csm: bool) -> int:
        """ Gives back how many different parts of speech are in the text. """
        pos_list: List[str] = [x.udep_upostag for x in TextComplexityService.current_graph_data.nodes]
        # TODO: visualize pos + pos density
        return len(set(pos_list))

    @staticmethod
    def how_many_punctuation(urn: str, is_csm: bool) -> int:
        """ Gives back how many different parts of speech are in the text. """
        return len([x for x in TextComplexityService.current_graph_data.nodes if x.udep_upostag == "PUNCT"])

    @staticmethod
    def how_many_sentences(urn: str, is_csm: bool) -> int:
        """Gives back the number of sentences in the text"""
        sentences_ids: List[int] = [AnnotationService.get_sentence_id(node) for node in
                                    TextComplexityService.current_graph_data.nodes]
        return len(set(sentences_ids))

    @staticmethod
    def how_many_sub_clauses(urn: str, is_csm: bool) -> int:
        """Gives back the number of subordinate clauses in the text. """
        aql: str = 'tok ->dep[deprel=/(acl|advcl|ccomp|xcomp)/] upostag="VERB"'
        node_ids: List[str] = CorpusService.find_matches(urn, aql, is_csm=is_csm)
        # TODO: degree of sub clauses; ellipsis not counted
        return round(len(node_ids) / 2)

    @staticmethod
    def how_many_types(urn: str, is_csm: bool) -> int:
        """ Gives back the numbers of types. """
        types: Set[str] = TextComplexityService.get_types()
        return len(types)

    @staticmethod
    def how_many_words(urn: str, is_csm: bool) -> int:
        """ Gives back the number of words in the text. """
        return len(TextComplexityService.current_graph_data.nodes)

    @staticmethod
    def lexical_density(urn: str, is_csm: bool) -> float:
        """ Gives back the lexical density of the text. """
        token_count: int = TextComplexityService.how_many_words(urn, is_csm)
        types: Set[str] = TextComplexityService.get_types()
        content_words: Set[str] = set()
        for word in types:
            if word not in TextService.stop_words_latin:
                content_words.add(word)
        return len(content_words) / token_count

    @staticmethod
    def text_complexity(measure: str, urn: str, is_csm: bool, gd: GraphData) -> TextComplexity:
        """ Defines the text complexity according to the kind of measure requested. """
        if is_csm:
            measure_map: Dict[str, callable] = TextComplexityService.get_measure_map()
            TextComplexityService.current_graph_data = gd
            tc: TextComplexity = TextComplexity()
            if measure == TextComplexityMeasure.all.name:
                for key in measure_map:
                    tc.__setattr__(key, round(measure_map[key](urn, is_csm), 2))
                tc.all = TextComplexityService.calculate_overall_complexity(tc)
            else:
                tc.__setattr__(measure, round(measure_map[measure](urn, is_csm), 2))
            return tc
        else:
            url: str = f"{Config.INTERNET_PROTOCOL}{Config.HOST_IP_CSM}:" + \
                       f"{Config.CORPUS_STORAGE_MANAGER_PORT}{Config.SERVER_URI_TEXT_COMPLEXITY}"
            ar: AnnisResponse = AnnisResponse(graph_data=gd)
            tcf: TextComplexityForm = TextComplexityForm(urn=urn, measure=TextComplexityMeasure.all.name,
                                                         annis_response=json.dumps(ar.to_dict()))
            response: requests.Response = requests.post(url, data=tcf.to_dict())
            return TextComplexity.from_dict(json.loads(response.text))
