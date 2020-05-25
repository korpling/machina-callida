from typing import List, Dict

from graphannis.cs import FrequencyTableEntry

from mcserver.app.services import AnnotationService
from mcserver.config import Config

from mcserver.app.models import Phenomenon, FrequencyAnalysis, FrequencyItem, GraphData, Dependency, LinkMC, NodeMC


class FrequencyService:
    """ Service for calculating word (or construction) frequencies in text corpora. """

    @staticmethod
    def add_case_frequencies(urn: str, search_phenomenon: List[Phenomenon]) -> FrequencyAnalysis:
        """ Adds frequency information for case annotations in a corpus. """
        aql: str = f"{Phenomenon.case.value}={Config.AQL_CASE} {Config.AQL_DEP} "
        definition: str = f"1:{search_phenomenon[0].value},2:"
        fa: FrequencyAnalysis = FrequencyAnalysis()
        if search_phenomenon[1] == Phenomenon.case:
            aql += f"{Phenomenon.case.value}={Config.AQL_CASE}"
            definition += search_phenomenon[1].value
            result: List[FrequencyTableEntry] = Config.CORPUS_STORAGE_MANAGER.frequency(
                corpus_name=urn, query=aql, definition=definition)
            fa += [FrequencyItem([x.values[0], x.values[1]], search_phenomenon, x.count) for x in result]
        else:
            aql += search_phenomenon[1].value
            definition += search_phenomenon[1].value
            result: List[FrequencyTableEntry] = Config.CORPUS_STORAGE_MANAGER.frequency(
                corpus_name=urn, query=aql, definition=definition)
            fa += [FrequencyItem([x.values[0], x.values[1]], search_phenomenon, x.count) for x in result]
        return fa

    @staticmethod
    def add_dependency_frequencies(graph_data: GraphData, fa: FrequencyAnalysis):
        """ Performs a frequency analysis for dependency annotations in a corpus. """
        id_to_node_dict: Dict[str, int] = {graph_data.nodes[i].id: i for i in range(len(graph_data.nodes))}
        dep_to_enum_dict: Dict[str, Dependency] = {}
        for key in AnnotationService.phenomenon_map[Phenomenon.dependency]:
            for value in AnnotationService.phenomenon_map[Phenomenon.dependency][key]:
                dep_to_enum_dict[value] = Dependency[key]
        dep_links: List[LinkMC] = [link for link in graph_data.links if
                                   link.annis_component_name == Config.GRAPHANNIS_DEPENDENCY_LINK]
        id_to_source_link_dict: Dict[str, List[LinkMC]] = {}
        for link in dep_links:
            id_to_source_link_dict[link.source] = id_to_source_link_dict.get(link.source, []) + [link]
        id_to_target_link_dict: Dict[str, List[LinkMC]] = {}
        for link in dep_links:
            id_to_target_link_dict[link.target] = id_to_target_link_dict.get(link.target, []) + [link]
        values_to_fi_dict: Dict[str, FrequencyItem] = {}
        for link in dep_links:
            base_node: NodeMC = graph_data.nodes[id_to_node_dict[link.source]]
            if not link.udep_deprel:
                continue
            dep: Dependency = dep_to_enum_dict[link.udep_deprel]
            FrequencyService.add_frequency_item(base_node, dep, values_to_fi_dict, 1)
            for other_link in id_to_source_link_dict.get(link.target, []):
                base_node = graph_data.nodes[id_to_node_dict[other_link.target]]
                FrequencyService.add_frequency_item(base_node, dep, values_to_fi_dict, 0)
                FrequencyService.increase_frequency_count(
                    [dep.name, dep_to_enum_dict[other_link.udep_deprel].name],
                    [Phenomenon.dependency, Phenomenon.dependency], values_to_fi_dict)
        for fi in values_to_fi_dict.values():
            fa.append(fi)

    @staticmethod
    def add_frequency_item(base_node: NodeMC, dep: Dependency, values_to_fi_dict: Dict[str, FrequencyItem],
                           target_index: int):
        """ Builds a collection of frequency items for given dependency links. """
        values_list: List[List[str]] = [[base_node.udep_feats], [base_node.udep_lemma], [base_node.udep_upostag]]
        phenomena_list: List[List[Phenomenon]] = [[Phenomenon.case], [Phenomenon.lemma], [Phenomenon.partOfSpeech]]
        for vl in values_list:
            vl.insert(target_index, dep.name)
        for pl in phenomena_list:
            pl.insert(target_index, Phenomenon.dependency)
        if not base_node.udep_feats or Phenomenon.case.name not in base_node.udep_feats.lower():
            values_list.pop(0)
            phenomena_list.pop(0)
        for i in range(len(values_list)):
            FrequencyService.increase_frequency_count(values_list[i], phenomena_list[i], values_to_fi_dict)

    @staticmethod
    def add_generic_frequencies(urn: str, search_phenomenon: List[Phenomenon]) -> FrequencyAnalysis:
        """ Adds frequency information for case and lemma annotations in a corpus. """
        aql: str = f"{search_phenomenon[0].value} {Config.AQL_DEP} "
        definition: str = f"1:{search_phenomenon[0].value},2:"
        fa: FrequencyAnalysis = FrequencyAnalysis()
        if search_phenomenon[1] == Phenomenon.case:
            aql += f"{Phenomenon.case.value}={Config.AQL_CASE}"
            definition += Phenomenon.case.value
            result: List[FrequencyTableEntry] = Config.CORPUS_STORAGE_MANAGER.frequency(
                corpus_name=urn, query=aql, definition=definition)
            fa += [FrequencyItem(x.values, search_phenomenon, x.count) for x in result]
        else:
            aql += search_phenomenon[1].value
            definition += search_phenomenon[1].value
            result: List[FrequencyTableEntry] = Config.CORPUS_STORAGE_MANAGER.frequency(
                corpus_name=urn, query=aql, definition=definition)
            fa += [FrequencyItem(x.values, search_phenomenon, x.count) for x in result]
        return fa

    @staticmethod
    def extract_case_values(fa: FrequencyAnalysis) -> FrequencyAnalysis:
        """ Checks if features were involved in the search and, if yes, extracts the case values from them. """
        values_to_fi_dict: Dict[str, List[FrequencyItem]] = {}
        for fi in fa:
            target_indices: List[int] = [i for i in range(len(fi.phenomena)) if fi.phenomena[i] == Phenomenon.case]
            for ti in target_indices:
                value_parts: List[str] = fi.values[ti].split("|")
                case_string: str = next(x for x in value_parts if Phenomenon.case.name in x.lower())
                fi.values[ti] = case_string.split("=")[1]
            values_combined: str = "".join(fi.values)
            values_to_fi_dict[values_combined] = values_to_fi_dict.get(values_combined, []) + [fi]
        ret_val: FrequencyAnalysis = FrequencyAnalysis()
        # remove duplicates that have the same values
        for key in values_to_fi_dict:
            new_fi: FrequencyItem = values_to_fi_dict[key][0]
            new_fi.count = sum(x.count for x in values_to_fi_dict[key])
            ret_val.append(new_fi)
        return ret_val

    @staticmethod
    def increase_frequency_count(values: List[str], phenomena: List[Phenomenon],
                                 values_to_fi_dict: Dict[str, FrequencyItem]):
        """ Increments frequency item counts for an existing collection. """
        values_combined: str = "".join(values)
        fi_default: FrequencyItem = FrequencyItem(values=values, phenomena=phenomena, count=0)
        fi_new: FrequencyItem = values_to_fi_dict.get(values_combined, fi_default)
        fi_new.count += 1
        values_to_fi_dict[values_combined] = fi_new
