import os
import subprocess
from enum import Enum
from sys import platform
from tempfile import mkstemp
from typing import Dict, List, Set, Tuple

import conllu
from conllu import TokenList
from graphannis.cs import CorpusStorageManager
from graphannis.graph import GraphUpdate
from networkx import MultiDiGraph, json_graph

from mcserver.app.models import Phenomenon, Case, PartOfSpeech, Dependency, Solution, ExerciseType, NodeMC, \
    ExerciseData, GraphData, LinkMC, TextPart
from mcserver.config import Config


class AnnotationService:
    """Service for adding annotations to raw texts."""

    excluded_annotations_set: Set[str] = {'form', 'id', 'head', Config.AQL_DEPREL}
    phenomenon_map: Dict[Enum, Dict[str, List[str]]] = {
        Phenomenon.case: {
            Case.ablative.name: ["Abl"],
            Case.accusative.name: ["Acc"],
            Case.dative.name: ["Dat"],
            Case.genitive.name: ["Gen"],
            Case.locative.name: ["Loc"],
            Case.nominative.name: ["Nom"],
            Case.vocative.name: ["Voc"],
        },
        Phenomenon.partOfSpeech: {
            PartOfSpeech.adjective.name: ["ADJ"],
            PartOfSpeech.adverb.name: ["ADV"],
            PartOfSpeech.auxiliary.name: ["AUX"],
            PartOfSpeech.conjunction.name: ["CCONJ", "SCONJ"],
            PartOfSpeech.interjection.name: ["INTJ"],
            PartOfSpeech.noun.name: ["NOUN"],
            PartOfSpeech.numeral.name: ["NUM"],
            PartOfSpeech.other.name: ["X"],
            PartOfSpeech.particle.name: ["PART"],
            PartOfSpeech.preposition.name: ["ADP"],
            PartOfSpeech.pronoun.name: ["DET", "PRON"],
            PartOfSpeech.properNoun.name: ["PROPN"],
            PartOfSpeech.punctuation.name: ["PUNCT"],
            PartOfSpeech.symbol.name: ["SYM"],
            PartOfSpeech.verb.name: ["VERB"],
        },
        Phenomenon.dependency: {
            Dependency.adjectivalClause.name: ["acl"],
            Dependency.adjectivalModifier.name: ["amod"],
            Dependency.adverbialClauseModifier.name: ["advcl"],
            Dependency.adverbialModifier.name: ["advmod"],
            Dependency.appositionalModifier.name: ["appos"],
            Dependency.auxiliary.name: ["aux", "aux:pass"],
            Dependency.caseMarking.name: ["case"],
            Dependency.classifier.name: ["clf"],
            Dependency.clausalComplement.name: ["ccomp", "xcomp"],
            Dependency.conjunct.name: ["conj"],
            Dependency.coordinatingConjunction.name: ["cc"],
            Dependency.copula.name: ["cop"],
            Dependency.determiner.name: ["det"],
            Dependency.discourseElement.name: ["discourse"],
            Dependency.dislocated.name: ["dislocated"],
            Dependency.expletive.name: ["expl"],
            Dependency.goesWith.name: ["goeswith"],
            Dependency.list.name: ["list"],
            Dependency.marker.name: ["mark"],
            Dependency.multiwordExpression.name: ["fixed", "flat", "flat:name", "compound"],
            Dependency.nominalModifier.name: ["nmod", "nmod:poss"],
            Dependency.numericModifier.name: ["nummod"],
            Dependency.object.name: ["obj", "obj:dir", "iobj"],
            Dependency.oblique.name: ["obl", "obl:agent"],
            Dependency.orphan.name: ["orphan"],
            Dependency.parataxis.name: ["parataxis"],
            Dependency.punctuation.name: ["punct"],
            Dependency.root.name: ["root"],
            Dependency.subject.name: ["nsubj", "nsubj:pass", "csubj", "csubj:pass"],
            Dependency.vocative.name: ["vocative"]
        },
        Phenomenon.lemma: {}}

    @staticmethod
    def add_urn_to_sentences(text_list: List[Tuple[str, str]], annotations: List[TokenList]) -> None:
        """ Adds the relevant URN for every annotated sentence. """
        current_text_list_index: int = 0
        current_start_index: int = 0
        for sent in annotations:
            first_token: str = sent.tokens[0]["form"]
            new_index: int = text_list[current_text_list_index][1].find(first_token, current_start_index)
            if new_index > -1:
                current_start_index = new_index + len(first_token)
            elif not first_token[-1].isalpha():
                # account for cases where the parser failed to tokenize correctly, thus appending punctuation to the
                # end of a regular word
                new_index = text_list[current_text_list_index][1].find(first_token[:-1], current_start_index)
                if new_index < 0:
                    continue
                else:
                    current_start_index = new_index + len(first_token)
            else:
                while new_index < 0 and len(text_list) > current_text_list_index:
                    current_text_list_index += 1
                    current_start_index = 0
                    new_index = text_list[current_text_list_index][1].find(first_token, current_start_index)
                    current_start_index = new_index + len(first_token)
            sent.metadata["urn"] = text_list[current_text_list_index][0]

    @staticmethod
    def get_citation_label(text_parts: List[TextPart], citation_values: List[int]) -> str:
        """ Builds composite citation labels from the respective values. """
        relevant_text_parts: List[TextPart] = [next(x for x in text_parts if x.citation.value == citation_values[0])]
        if len(citation_values) > 1:
            relevant_text_parts.append(
                next(x for x in relevant_text_parts[0].sub_text_parts if x.citation.value == citation_values[1]))
            if len(citation_values) > 2:
                relevant_text_parts.append(
                    next(x for x in relevant_text_parts[1].sub_text_parts if x.citation.value == citation_values[2]))
        return ".".join(x.citation.label for x in relevant_text_parts)

    @staticmethod
    def get_disk_urn(urn: str) -> str:
        """ Modifies a URN so it can be used as a cross-platform file name. """
        return urn.replace(":", "_")

    @staticmethod
    def get_sentence_id(node: NodeMC) -> int:
        """ Retrieves the sentence ID for a given node from its node ID. """
        return int(node.id.split("#")[-1].split("tok")[0].replace("sent", ""))

    @staticmethod
    def get_single_subgraph(disk_urn: str, node_ids: List[str], ctx_left: int = 5, ctx_right: int = 5,
                            is_csm: bool = False) -> GraphData:
        """ Retrieves a single subgraph for a given URN and node IDs. """
        if not is_csm:
            raise NotImplementedError
        mdg: MultiDiGraph = Config.CORPUS_STORAGE_MANAGER.subgraph(corpus_name=disk_urn, node_ids=node_ids,
                                                                   ctx_left=ctx_left, ctx_right=ctx_right)
        graph_data_raw: dict = json_graph.node_link_data(mdg)
        return AnnotationService.map_graph_data(graph_data_raw)

    @staticmethod
    def get_udpipe(text: str, need_parse: bool = True, file_dict: dict = None) -> str:
        """Annotate a string of raw text and return the result as string."""
        model_path = Config.UDPIPE_MODEL_PATH
        udpipe_path = Config.UDPIPE_PATH_OSX if platform == Config.PLATFORM_MACOS else (
            Config.UDPIPE_PATH_WIN64 if platform == Config.PLATFORM_WINDOWS else Config.UDPIPE_PATH_LINUX)
        if file_dict is None:
            file_dict: dict = {}
            input_bytes = bytearray(text, encoding='utf-8', errors='strict')
            file_handler, file_path = mkstemp()
            os.write(file_handler, input_bytes)
            file_dict[file_path] = file_handler
        files_string = " ".join([filePath for filePath in file_dict])
        # suppress error messages because UdPipe tends to send non-error informational stuff via StdErr
        with open(os.devnull, "w") as dev_null:
            result_bytes: bytes = subprocess.check_output(
                "{0} --tokenize --tag{1} {2} {3}".format(udpipe_path, " --parse" if need_parse else "", model_path,
                                                         files_string), shell=True, stderr=dev_null)
        for path in file_dict:
            os.close(file_dict[path])
            os.remove(path)
        result_string: str = result_bytes.decode('utf-8')
        return result_string

    @staticmethod
    def has_urn_sentence_range(urn: str) -> bool:
        """ Checks whether a URN refers to specific sentences or a whole text passage. """
        return "@" in urn

    @staticmethod
    def map_conll_to_graph(corpus_name: str, conll: List[TokenList], cs: CorpusStorageManager, file_name: str):
        """ Saves an annotated corpus in CONLL format to the ANNIS corpus storage. """
        # delete any existing corpus with this name
        cs.delete_corpus(file_name)
        # currently there is only one document because texts are their own corpus
        doc_name = 'doc1'
        with GraphUpdate() as g:
            doc_path = corpus_name + '/' + doc_name
            # create a corpus and document node
            # both nodes belong to the corpus graph, not the annotation graph
            g.add_node(node_name=corpus_name, node_type="corpus")
            g.add_node(node_name=doc_path, node_type="corpus")
            # the document is part of the corpus
            g.add_edge(doc_path, corpus_name, 'annis', 'PartOf', '')
            tok_before = None
            for tokenList in conll:
                conllid_to_annisid = dict()
                # create the sentence ID
                sentence_id: int = tokenList.metadata["sent_id"]
                sentence_node_name: str = f"{tokenList.metadata['urn']}/{doc_name}#sent{sentence_id}"
                # add nodes
                for tok in tokenList.tokens:
                    token_id: int = tok["id"]
                    # map CONLL to graphANNIS
                    tok_id_final = sentence_node_name + "tok{0}".format(token_id)
                    conllid_to_annisid[tok['id']] = tok_id_final
                    AnnotationService.map_token(tok, tok_id_final, g)
                    # a token belongs to its document
                    g.add_edge(tok_id_final, doc_path, 'annis', 'PartOf', '')
                    if tok_before is not None:
                        # add ordering edge between the tokens
                        g.add_edge(tok_before, tok_id_final, 'annis', 'Ordering', '')
                    # remember the current token for the next iteration
                    tok_before = tok_id_final
                # add pointing relations
                for tok in tokenList.tokens:
                    if 'head' in tok:
                        if tok['head'] != 0:
                            tok_id_source = conllid_to_annisid[tok['head']]
                            tok_id_target = conllid_to_annisid[tok['id']]

                            g.add_edge(tok_id_source, tok_id_target, '', 'Pointing', 'dep')
                            if Config.AQL_DEPREL in tok:
                                g.add_edge_label(tok_id_source, tok_id_target, '', 'Pointing', 'dep', 'udep',
                                                 Config.AQL_DEPREL, tok[Config.AQL_DEPREL])
            cs.apply_update(file_name, g)

    @staticmethod
    def map_graph_data(graph_data_raw: dict) -> GraphData:
        """ Creates a GraphData object from a Dict (that was created from networkX / JSON data). """
        # start copying the simple values to the final graph object
        graph_data: GraphData = GraphData(links=[], nodes=[], directed=graph_data_raw["directed"],
                                          graph=graph_data_raw["graph"], multigraph=graph_data_raw["multigraph"])
        # map the link data to our data model and add it to the graph
        for link in graph_data_raw["links"]:
            graph_data.links.append(LinkMC(annis_component_name=link["annis::component_name"],
                                           annis_component_type=link["annis::component_type"],
                                           source=link["source"],
                                           target=link["target"],
                                           udep_deprel=link.get(f"udep::deprel", None)))
        # map the nodes to our data model
        for node in graph_data_raw["nodes"]:
            # ignore malformed nodes
            if node.get("id", None) == 1:
                continue
            graph_data.nodes.append(AnnotationService.map_node(node))
        AnnotationService.sort_nodes(graph_data)
        return graph_data

    @staticmethod
    def map_graph_data_to_exercise(graph_data_raw: Dict, xml_guid: str, solutions: List[Solution]):
        """ Creates an ExerciseData object from the separate parts. """
        # create the basis for the download URL
        xml_url = "/" + xml_guid
        graph_data: GraphData = AnnotationService.map_graph_data(graph_data_raw)
        return ExerciseData(graph=graph_data, solutions=solutions, uri=xml_url)

    @staticmethod
    def map_node(node: dict):
        """ Maps a node dictionary to the native NodeMC class. """
        return NodeMC(annis_node_name=node["annis::node_name"], annis_node_type=node["annis::node_type"],
                      annis_tok=node.get("annis::tok", None), annis_type=node.get("annis::type", None),
                      id=str(node.get("id", "")), udep_lemma=node.get("udep::lemma", None),
                      udep_upostag=node.get("udep::upostag", None), udep_xpostag=node.get("udep::xpostag", None),
                      udep_feats=node.get("udep::feats", None))

    @staticmethod
    def map_search_values_to_aql(search_values_list: List[str], exercise_type: ExerciseType):
        """Maps raw pseudo-AQL to the real AQL, depending on the annotation backend and AQL syntax."""
        aqls: List[str] = []
        aql_parts: List[str] = []
        for i in range(len(search_values_list)):
            search_parts: List[str] = search_values_list[i].split("=")
            phenomenon: Phenomenon = Phenomenon[search_parts[0]]
            raw_values: List[str] = search_parts[1].split("|")
            aql_base: str
            if phenomenon == Phenomenon.dependency:
                aql_base = f'node {Config.AQL_DEP}[{Config.AQL_DEPREL}=' + "{0}] node"
            else:
                aql_base = phenomenon.value + '={0}'
            if phenomenon == Phenomenon.lemma:
                for rv in raw_values:
                    # need to prepare the mapping dynamically, so we can handle the following steps in a uniform way
                    AnnotationService.phenomenon_map[phenomenon][rv] = [rv]
            for rv in raw_values:
                translated_values: List[str] = AnnotationService.phenomenon_map[phenomenon][rv]
                aql_part: str
                if phenomenon == Phenomenon.case:
                    aql_part = aql_base.format('/.*Case={0}.*/'.format(translated_values[0]))
                else:
                    aql_part = aql_base.format(f'"{translated_values[0]}"' if len(
                        translated_values) == 1 else f"/({'|'.join(translated_values)})/")
                if AnnotationService.phenomenon_map[Phenomenon.dependency][Dependency.root.name][0] in aql_part:
                    aql_part = 'deps="{0}"'.format(
                        AnnotationService.phenomenon_map[Phenomenon.dependency][Dependency.root.name][0])
                aql_parts.append(aql_part)
        if exercise_type == ExerciseType.matching:
            final_aql: str = f'{aql_parts[0]} {Config.AQL_DEP} {aql_parts[1]}'
            if final_aql.count(f"{Config.AQL_DEP}[") == 2 or final_aql.count(f"{Config.AQL_DEP}[") + final_aql.count(
                    "deps=") == 2 or Config.AQL_DEPREL in \
                    aql_parts[1]:
                # too many dependencies involved, need to get the relations straight
                final_aql = final_aql.replace(f"{Config.AQL_DEP} node ", "")
            aqls.append(final_aql)
        else:
            aqls += aql_parts
        return aqls

    @staticmethod
    def map_token(tok, tok_id: str, g: GraphUpdate):
        """ Maps a token's annotations to the graphANNIS format. """
        g.add_node(tok_id)
        # this is an annotation node
        g.add_node_label(tok_id, 'annis', 'type', 'node')
        # it also has a token value
        g.add_node_label(tok_id, 'annis', 'tok', tok['form'])
        for k, v in tok.items():
            if k == "feats" and tok[k]:
                v = "|".join("{0}={1}".format(k2, v2) for k2, v2 in tok[k].items())
            # some of these were already dealt with, only add the 'new' annotations
            if isinstance(v, str) and k not in AnnotationService.excluded_annotations_set:
                g.add_node_label(tok_id, 'udep', k, v)

    @staticmethod
    def parse_conll_string(conll: str):
        """Parses a CONLL string and adds dependency annotations for root words as additional node annotations.
        This way, we can search for them later."""
        # parse CONLL
        annotations: List[TokenList] = conllu.parse(conll)
        # add root dependencies as separate node annotations
        for token_list in annotations:
            for token in token_list:
                if token["head"] == 0:
                    token["deps"] = token[Config.AQL_DEPREL]
        return annotations

    @staticmethod
    def sort_nodes(graph_data: GraphData):
        """Sorts the nodes according to the ordering links, i.e. by their tokens' occurrence in the text."""
        # if there is nothing to sort, return the object as is
        if len(graph_data.nodes) == 0:
            return graph_data
        # create a lookup dict so we can retrieve nodes faster
        node_id_to_index_dict: Dict[str, int] = {}
        for i in range(len(graph_data.nodes)):
            node_id_to_index_dict[graph_data.nodes[i].id] = i
        # get all ordering links
        ordering_links: List[LinkMC] = [x for x in graph_data.links if x.annis_component_type == "Ordering"]
        # get a list of all node IDs
        node_id_set: Set[str] = set([x.id for x in graph_data.nodes])
        # create set for ordering link targets
        target_set: Set[str] = set(map(lambda x: x.target, ordering_links))
        # look for the node of the first token in the text, i.e. the one that is not a target of any ordering link
        source_node_id: str = list(node_id_set ^ target_set)[0]
        # create a copy of the nodes so wen can change their order and then add them back to the graph
        nodes: List[NodeMC] = graph_data.nodes
        # clear the previous node order
        graph_data.nodes = []
        # create a lookup table so we can retrieve ordering links easily by their source value / node id
        ordering_link_source_to_index_dict: Dict[str, int] = {}
        for i in range(len(ordering_links)):
            ordering_link_source_to_index_dict[ordering_links[i].source] = i
        # repeat the process until we have processed one node for each ordering link (+ 1 initial node)
        while len(graph_data.nodes) <= len(ordering_links):
            graph_data.nodes.append(nodes[node_id_to_index_dict[source_node_id]])
            # check if there are more nodes to be processed
            if source_node_id not in ordering_link_source_to_index_dict:
                break
            ordering_link: LinkMC = ordering_links[ordering_link_source_to_index_dict[source_node_id]]
            source_node_id = ordering_link.target
