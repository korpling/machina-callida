import sys
import rapidjson as json
import os
from typing import List, Union, Set, Tuple
import requests
from MyCapytain.retrievers.cts5 import HttpCtsRetriever
from conllu import TokenList
from graphannis import CAPI, ffi
from graphannis.cs import ResultOrder
from graphannis.errors import consume_errors, NoSuchCorpus, GraphANNISException
from graphannis.util import node_name_from_match
from lxml import etree
from networkx import graph, MultiDiGraph
from networkx.readwrite import json_graph
from requests import HTTPError

from mcserver.app import db
from mcserver.app.models import CitationLevel, GraphData, Solution, ExerciseType, Phenomenon, FrequencyAnalysis, \
    AnnisResponse, SolutionElement, CorpusMC
from mcserver.app.services import AnnotationService, XMLservice, TextService, FileService, FrequencyService, \
    CustomCorpusService
from mcserver.config import Config
from mcserver.models_auto import Corpus


class CorpusService:
    """Service for handling corpora/texts. Performs CRUD-like operations on the database."""

    existing_corpora: List[Corpus] = []

    @staticmethod
    def add_citation_levels(corpus: Corpus, citation_levels: List[Union[CitationLevel, str]]):
        """Adds additional citation levels to a corpus."""
        if len(citation_levels) > 1:
            corpus.citation_level_2 = citation_levels[1] if isinstance(citation_levels[1], str) else citation_levels[
                1].value
            if len(citation_levels) > 2:
                corpus.citation_level_3 = citation_levels[2] if isinstance(citation_levels[2], str) else \
                    citation_levels[2].value

    @staticmethod
    def add_corpus(title_value: str, urn: str, group_name_value: str,
                   citation_levels: List[Union[CitationLevel, str]]) -> None:
        """Adds a new corpus to the database."""
        new_corpus = CorpusMC.from_dict(title=title_value, source_urn=urn, author=group_name_value,
                                        citation_level_1=citation_levels[0])
        CorpusService.add_citation_levels(new_corpus, citation_levels)
        db.session.add(new_corpus)
        # need to commit once so the Corpus ID (cid) gets generated by the database
        db.session.commit()
        # now we can build the URI from the Corpus ID
        new_corpus.uri = "/{0}".format(new_corpus.cid)
        db.session.commit()

    @staticmethod
    def find_matches(urn: str, aql: str, is_csm: bool = False) -> List[str]:
        """ Finds matches for a given URN and AQL and returns the corresponding node IDs. """
        if is_csm:
            disk_urn: str = AnnotationService.get_disk_urn(urn)
            result_list: List[List[str]]
            try:
                result_list = Config.CORPUS_STORAGE_MANAGER.find(corpus_name=disk_urn, query=aql, limit=sys.maxsize,
                                                                 order=ResultOrder.NotSorted)
            except NoSuchCorpus:
                CorpusService.get_corpus(urn, True)
                result_list = Config.CORPUS_STORAGE_MANAGER.find(corpus_name=disk_urn, query=aql, limit=sys.maxsize,
                                                                 order=ResultOrder.NotSorted)
            # extract the SALT ID for each match
            return [y for x in node_name_from_match(result_list) for y in x]
        else:
            url: str = Config.INTERNET_PROTOCOL + f"{Config.HOST_IP_CSM}:{Config.CORPUS_STORAGE_MANAGER_PORT}" + \
                       Config.SERVER_URI_ANNIS_FIND
            response: requests.Response = requests.get(url, params=dict(urn=urn, aql=aql))
            return json.loads(response.text)

    @staticmethod
    def get_annotations_from_string(annotations_or_urn: str) -> List[TokenList]:
        """ Retrieves annotations from a string by either parsing it or looking up the relevant corpus by its URN. """
        conll: List[TokenList]
        if CustomCorpusService.is_custom_corpus_urn(annotations_or_urn):
            if CustomCorpusService.is_custom_corpus_proiel(annotations_or_urn):
                conll = CustomCorpusService.get_treebank_annotations(annotations_or_urn)
            else:
                conll = CustomCorpusService.get_custom_corpus_annotations(annotations_or_urn)
        else:
            if CorpusService.is_urn(annotations_or_urn):
                raw_text: str = CorpusService.get_raw_text(urn=annotations_or_urn, is_csm=True)
                annotations_or_urn = AnnotationService.get_udpipe(raw_text)
            # parse CONLL and add root dependencies as separate node annotations
            conll = AnnotationService.parse_conll_string(annotations_or_urn)
        return conll

    @staticmethod
    def get_corpus(cts_urn: str, is_csm: bool) -> AnnisResponse:
        """ Loads the text for a standard corpus from the CTS API or cache. """
        if is_csm:
            # get graph data for further processing
            graph_data_raw: dict = CorpusService.get_graph_data(cts_urn)
            if not graph_data_raw:
                return AnnisResponse()
            graph_data: GraphData = AnnotationService.map_graph_data(graph_data_raw)
            ar: AnnisResponse = AnnisResponse(solutions=[], uri="", exercise_id="", graph_data=graph_data)
            return ar
        else:
            # there is actually no text, only a URN, so we need to get it ourselves
            url: str = f"{Config.INTERNET_PROTOCOL}{Config.HOST_IP_CSM}:{Config.CORPUS_STORAGE_MANAGER_PORT}/"
            response: requests.Response = requests.get(url, params=dict(urn=cts_urn))
            return AnnisResponse(json_dict=json.loads(response.text))

    @staticmethod
    def get_frequency_analysis(urn: str, is_csm: bool) -> FrequencyAnalysis:
        """ Collects frequency statistics for various combinations of linguistic annotations in a corpus. """
        if is_csm:
            ar: AnnisResponse = CorpusService.get_corpus(urn, is_csm)
            gd: GraphData = GraphData(json_dict=ar.__dict__)
            search_phenomena: List[List[Phenomenon]] = []
            for head_phenomenon in Phenomenon:
                for base_phenomenon in Phenomenon:
                    search_phenomena.append([head_phenomenon, base_phenomenon])
            disk_urn: str = AnnotationService.get_disk_urn(urn)
            fa: FrequencyAnalysis = FrequencyAnalysis()
            for search_phenomenon in search_phenomena:
                if Phenomenon.dependency in search_phenomenon:
                    continue
                elif search_phenomenon[0] == Phenomenon.case:
                    fa += FrequencyService.add_case_frequencies(disk_urn, search_phenomenon)
                elif search_phenomenon[0] in [Phenomenon.lemma, Phenomenon.partOfSpeech]:
                    fa += FrequencyService.add_generic_frequencies(disk_urn, search_phenomenon)
            FrequencyService.add_dependency_frequencies(gd, fa)
            return FrequencyService.extract_case_values(fa)
        else:
            url: str = Config.INTERNET_PROTOCOL + f"{Config.HOST_IP_CSM}:{Config.CORPUS_STORAGE_MANAGER_PORT}" + \
                       Config.SERVER_URI_FREQUENCY
            response: requests.Response = requests.get(url, params=dict(urn=urn))
            return FrequencyAnalysis(json_list=json.loads(response.text))

    @staticmethod
    def get_graph(cts_urn: str) -> MultiDiGraph:
        """ Retrieves a graph from the cache or, if not there, builds it from scratch. """
        cts_urn_disk: str = AnnotationService.get_disk_urn(cts_urn)
        cts_urn_raw: str = cts_urn.split("@")[0] if AnnotationService.has_urn_sentence_range(cts_urn) else cts_urn
        # need to adjust the URN so it can be used as a cross-platform file name
        cts_urn_raw_disk: str = AnnotationService.get_disk_urn(cts_urn_raw)
        annotations: List[TokenList]
        mdg: MultiDiGraph
        doc_id: str = cts_urn + '/doc1'
        if CustomCorpusService.is_custom_corpus_proiel(cts_urn):
            try:
                mdg = Config.CORPUS_STORAGE_MANAGER.subcorpus_graph(corpus_name=cts_urn_disk, document_ids=[doc_id])
                return mdg
            except (NoSuchCorpus, GraphANNISException):
                annotations = CustomCorpusService.get_treebank_annotations(cts_urn)
                AnnotationService.map_conll_to_graph(corpus_name=cts_urn, conll=annotations,
                                                     cs=Config.CORPUS_STORAGE_MANAGER, file_name=cts_urn_disk)
                mdg = Config.CORPUS_STORAGE_MANAGER.subcorpus_graph(corpus_name=cts_urn_disk, document_ids=[doc_id])
                return mdg
        try:
            mdg = Config.CORPUS_STORAGE_MANAGER.subcorpus_graph(cts_urn_disk, [doc_id])
            return mdg
        except (NoSuchCorpus, GraphANNISException):
            doc_id = cts_urn_raw + '/doc1'
            try:
                mdg = Config.CORPUS_STORAGE_MANAGER.subcorpus_graph(cts_urn_raw_disk, [doc_id])
            except (NoSuchCorpus, GraphANNISException):
                text_list: List[Tuple[str, str]] = CorpusService.load_text_list(cts_urn_raw=cts_urn_raw)
                raw_text: str = TextService.strip_whitespace(" ".join([x[1] for x in text_list]))
                annotations_conll: str = AnnotationService.get_udpipe(raw_text)
                # parse CONLL and add root dependencies as separate node annotations
                annotations = AnnotationService.parse_conll_string(annotations_conll)
                AnnotationService.add_urn_to_sentences(text_list, annotations)
                # each document gets its own corpus
                AnnotationService.map_conll_to_graph(cts_urn_raw, annotations, Config.CORPUS_STORAGE_MANAGER,
                                                     cts_urn_raw_disk)
                mdg = Config.CORPUS_STORAGE_MANAGER.subcorpus_graph(cts_urn_raw_disk, [doc_id])
        if AnnotationService.has_urn_sentence_range(cts_urn):
            return CorpusService.get_sentence_range(mdg=mdg, cts_urn=cts_urn, file_name=cts_urn_disk)
        return mdg

    @staticmethod
    def get_graph_data(cts_urn: str) -> dict:
        """ Retrieves graph data for a graph. """
        if not cts_urn:
            return {}
        mdg: MultiDiGraph = CorpusService.get_graph(cts_urn)
        return {} if not mdg else json_graph.node_link_data(mdg)

    @staticmethod
    def get_matches(urn: str, aqls: List[str], search_phenomena: List[Phenomenon]) -> List[Solution]:
        """ Searches for results for a given AQL query and presents the matches as a list of SALT IDs. """
        # model matches as the basis for solutions so we can process them more easily later on
        matches: List[Solution] = []
        for aql in aqls:
            node_ids: List[str] = CorpusService.find_matches(urn, aql, is_csm=True)
            if len(search_phenomena) == 1:
                # it's cloze or markWords; the solutions only have a target, no explicit value
                if search_phenomena[0] == Phenomenon.dependency:
                    node_ids = [node_ids[i] for i in range(len(node_ids)) if i % 2 != 0]
                    matches += [Solution(target=SolutionElement(salt_id=x)) for x in node_ids]
                else:
                    matches += [Solution(target=SolutionElement(salt_id=x)) for x in node_ids]
            else:
                # it's a matching exercise
                if search_phenomena[0] == Phenomenon.dependency:
                    for i in range(len(node_ids)):
                        if i % 3 == 0:
                            matches.append(Solution(target=SolutionElement(salt_id=node_ids[i + 1]),
                                                    value=SolutionElement(salt_id=node_ids[i + 2])))
                else:
                    for i in range(len(node_ids)):
                        if i % 2 == 0:
                            matches.append(Solution(target=SolutionElement(salt_id=node_ids[i]),
                                                    value=SolutionElement(salt_id=node_ids[i + 1])))
        from operator import attrgetter
        matches.sort(key=attrgetter("target.sentence_id", "target.token_id"))
        return matches

    @staticmethod
    def get_raw_text(urn: str, is_csm: bool):
        """ Retrieves the raw text for a corpus. """
        ar: AnnisResponse = CorpusService.get_corpus(cts_urn=urn, is_csm=is_csm)
        graph_data: GraphData = GraphData(json_dict=ar.__dict__)
        text_raw = " ".join(x.annis_tok for x in graph_data.nodes)
        # remove the spaces before punctuation because, otherwise, the parser won't work correctly
        return TextService.strip_whitespace(text_raw)

    @staticmethod
    def get_sentence_range(mdg: MultiDiGraph, cts_urn: str, file_name: str) -> MultiDiGraph:
        """ Retrieves part of a larger graph, according to a URN with sentence IDs. """
        sentence_range: List[int] = list(map(lambda x: int(x), cts_urn.split("@")[1].split("-")))
        graph_data_raw: dict = json_graph.node_link_data(mdg)
        graph_data: GraphData = AnnotationService.map_graph_data(graph_data_raw)
        substring: str = ""
        node_urns: List[str] = []
        for node in graph_data.nodes:
            sentence_id: int = AnnotationService.get_sentence_id(node)
            node_urns.append(node.id.split("/")[1])
            substring += (" " + node.annis_tok) if sentence_range[0] <= sentence_id <= sentence_range[1] else ""
        substring = TextService.strip_whitespace(substring)
        # parse CONLL and add root dependencies as separate node annotations
        annotations: List[TokenList] = AnnotationService.parse_conll_string(AnnotationService.get_udpipe(substring))
        # add URNs for every sentence by relying on the graph data
        tok_count: int = 0
        for sent in annotations:
            sent.metadata["urn"] = node_urns[tok_count]
            tok_count += len(sent.tokens)
        # each document gets its own corpus
        AnnotationService.map_conll_to_graph(cts_urn, annotations, Config.CORPUS_STORAGE_MANAGER, file_name)
        return Config.CORPUS_STORAGE_MANAGER.subcorpus_graph(file_name, [cts_urn + '/doc1'])

    @staticmethod
    def get_standard_corpus_reff(cts_urn: str) -> List[str]:
        """ Loads valid references for a standard corpus from the CTS API. """
        disk_urn: str = AnnotationService.get_disk_urn(cts_urn)
        disk_reff = FileService.get_reff_from_disk(disk_urn)
        if not disk_reff:
            resolver: HttpCtsRetriever = HttpCtsRetriever(Config.CTS_API_BASE_URL)
            resp: str = ""
            try:
                resp = resolver.getValidReff(urn=cts_urn)
            except (HTTPError, requests.exceptions.ConnectionError):
                return []
            xml: etree.Element = etree.fromstring(resp)
            XMLservice.strip_name_spaces(xml)
            disk_reff: List[str] = xml.xpath("/GetValidReff/reply/reff//text()")
            with open(os.path.join(Config.REFF_CACHE_DIRECTORY, disk_urn), "w+") as f:
                f.write(json.dumps(disk_reff))
        return disk_reff

    @staticmethod
    def get_subgraph(urn: str, aql: str, ctx_left: int = 5, ctx_right: int = 5, is_csm: bool = False) -> AnnisResponse:
        """ Retrieves subgraph data for a given URN and node IDs. """
        disk_urn: str = AnnotationService.get_disk_urn(urn)
        if is_csm:
            node_ids: List[str] = CorpusService.find_matches(urn, aql, is_csm=is_csm)
            gd: GraphData = AnnotationService.get_single_subgraph(disk_urn, node_ids, ctx_left, ctx_right, is_csm)
            return AnnisResponse(solutions=[], uri="", exercise_id="", graph_data=gd)
        else:
            url: str = Config.INTERNET_PROTOCOL + f"{Config.HOST_IP_CSM}:{Config.CORPUS_STORAGE_MANAGER_PORT}" + \
                       Config.SERVER_URI_CSM_SUBGRAPH
            response: requests.Response = requests.get(url, params=dict(urn=disk_urn, aqls=aql,
                                                                        ctx_left=ctx_left, ctx_right=ctx_right))
            return AnnisResponse(json_dict=json.loads(response.text))

    @staticmethod
    def init_graphannis_logging() -> None:
        """Initializes logging for the graphannis backend."""
        err = ffi.new("AnnisErrorList **")
        CAPI.annis_init_logging(os.path.join(os.getcwd(), Config.GRAPHANNIS_LOG_PATH).encode("utf-8"), CAPI.Info,
                                err)  # Debug
        consume_errors(err)

    @staticmethod
    def is_urn(maybe_urn: str):
        """ Checks if the string represents a URN. """
        return maybe_urn.startswith("urn:")

    @staticmethod
    def load_text_list(cts_urn_raw: str) -> List[Tuple[str, str]]:
        """ Loads the text list for a new corpus. """
        if CustomCorpusService.is_custom_corpus_urn(cts_urn_raw):
            # this is a custom corpus, e.g. the VIVA textbook
            return CustomCorpusService.get_custom_corpus_text(cts_urn_raw)
        else:
            resolver: HttpCtsRetriever = HttpCtsRetriever(Config.CTS_API_BASE_URL)
            resp: str
            try:
                resp = resolver.getPassage(urn=cts_urn_raw)
            except (HTTPError, requests.exceptions.ConnectionError):
                return []
            xml: etree.Element = etree.fromstring(resp)
            XMLservice.strip_name_spaces(xml)
            return XMLservice.get_text_parts_by_urn(cts_urn_raw, xml)

    @staticmethod
    def process_corpus_data(urn: str, annotations: List[TokenList], aqls: List[str],
                            exercise_type: ExerciseType, search_phenomena: List[Phenomenon]) -> dict:
        """Listens for calls to the corpus storage manager and processes data for incoming connections."""
        G: graph = CorpusService.get_graph(urn)
        # execute query and remember all matching nodes
        solutions: List[Solution] = CorpusService.get_matches(urn, aqls, search_phenomena)
        # remove the annotations for the matching tokens in the subgraph but remember their values
        if exercise_type in [ExerciseType.cloze, ExerciseType.markWords]:
            for match in solutions:
                # remember the correct value before removing it; cloze/markWords solutions only have a target, no value
                match.target.content = G.nodes[match.target.salt_id]['annis::tok']
        # get graph data for further processing
        graph_data_raw: dict = json_graph.node_link_data(G)
        # serialize the updated CONLL to string format so we can add the updated annotations to the database
        text_conll: str = ""
        for x in annotations:
            # "newpar" with value "None" cannot be handled properly, so just delete it
            if "newpar" in x.metadata and not x.metadata["newpar"]:
                del x.metadata["newpar"]
            text_conll += x.serialize()
        return dict(graph_data_raw=graph_data_raw, solutions=[x.serialize() for x in solutions], conll=text_conll)

    @staticmethod
    def update_corpora():
        """Checks the remote repositories for new corpora to be included in our database."""
        CorpusService.existing_corpora = db.session.query(Corpus).all()
        resolver: HttpCtsRetriever = HttpCtsRetriever(Config.CTS_API_BASE_URL)
        # check the appropriate literature for the desired author
        resp: str = resolver.getCapabilities(urn="urn:cts:latinLit")  # "urn:cts:greekLit" for Greek
        xml: etree.Element = etree.fromstring(resp)
        XMLservice.strip_name_spaces(xml)
        ti = xml.find("./reply/TextInventory")
        urn_set_existing: Set[str] = set([x.source_urn for x in CorpusService.existing_corpora])
        # we want to keep custom corpora, so add them to the new set first
        urn_set_new: Set[str] = set(x.corpus.source_urn for x in CustomCorpusService.custom_corpora)
        for textGroup in ti:
            group_name = textGroup.find("./groupname")
            group_name_value: str = group_name.text
            for work in textGroup.findall("./work"):
                edition = work.find("./edition")
                if edition is None:
                    continue
                citations = edition.findall("./online/citationMapping//citation")
                citation_levels: List[Union[CitationLevel, str]] = []
                for i in range(len(citations)):
                    citation_levels.append(citations[i].get("label"))
                urn = edition.get("urn")
                urn_set_new.add(urn)
                title = work.find("./title")
                title_value = title.text
                if urn not in urn_set_existing:
                    CorpusService.add_corpus(title_value, urn, group_name_value, citation_levels)
                else:
                    corpus_to_update: Corpus = db.session.query(Corpus).filter_by(source_urn=urn).first()
                    CorpusService.update_corpus(title_value, urn, group_name_value, citation_levels, corpus_to_update)
        for urn in urn_set_existing:
            if urn not in urn_set_new:
                corpus_to_delete: Corpus = db.session.query(Corpus).filter_by(source_urn=urn).first()
                db.session.delete(corpus_to_delete)
                db.session.commit()
        CorpusService.existing_corpora = db.session.query(Corpus).all()

    @staticmethod
    def update_corpus(title_value: str, urn: str, author: str,
                      citation_levels: List[Union[CitationLevel, str]], corpus_to_update: Corpus):
        """Updates a single corpus by changing its properties to the given values, if necessary."""
        if corpus_to_update.title == title_value and corpus_to_update.author == author and \
                corpus_to_update.source_urn == urn and \
                [corpus_to_update.citation_level_1, corpus_to_update.citation_level_2,
                 corpus_to_update.citation_level_3] == citation_levels:
            return
        corpus_to_update.title = title_value
        corpus_to_update.author = author
        corpus_to_update.citation_level_1 = citation_levels[0]
        corpus_to_update.source_urn = urn
        CorpusService.add_citation_levels(corpus_to_update, citation_levels)
        db.session.commit()
