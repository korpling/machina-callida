from typing import List, Dict

from graphannis.cs import FrequencyTableEntry

from mcserver.app.services import AnnotationService
from mcserver.config import Config

from mcserver.app.models import Phenomenon, FrequencyItem, GraphData, Dependency, LinkMC, NodeMC, Feats


class FrequencyService:
    """ Service for calculating word (or construction) frequencies in text corpora. """

    @staticmethod
    def add_case_frequencies(urn: str, search_phenomena: List[Phenomenon]) -> List[FrequencyItem]:
        """ Adds frequency information for all case annotations in a corpus. """
        aql: str = f"{Phenomenon.FEATS}={Config.AQL_CASE} {Config.AQL_DEP} "
        definition: str = f"1:{search_phenomena[0]},2:"
        fa: List[FrequencyItem] = []
        if search_phenomena[1] == Phenomenon.FEATS:
            aql += f"{Phenomenon.FEATS}={Config.AQL_CASE}"
            fa += FrequencyService.add_case_frequency_items(urn, aql, definition, search_phenomena)
        else:
            aql += search_phenomena[1]
            fa += FrequencyService.add_case_frequency_items(urn, aql, definition, search_phenomena)
        return fa

    @staticmethod
    def add_case_frequency_items(urn: str, aql: str, definition: str, search_phenomena: List[Phenomenon]) -> \
            List[FrequencyItem]:
        """Adds frequency information for specific case annotations in a corpus."""
        definition += search_phenomena[1]
        result: List[FrequencyTableEntry] = Config.CORPUS_STORAGE_MANAGER.frequency(
            corpus_name=urn, query=aql, definition=definition)
        return [FrequencyItem(x.count, search_phenomena, [x.values[0], x.values[1]]) for x in
                result]

    @staticmethod
    def add_dependency_frequencies(graph_data: GraphData, fa: List[FrequencyItem]):
        """ Performs a frequency analysis for dependency annotations in a corpus. """
        id_to_node_dict: Dict[str, int] = {graph_data.nodes[i].id: i for i in range(len(graph_data.nodes))}
        dep_to_enum_dict: Dict[str, Dependency] = {}
        for key in AnnotationService.phenomenon_map[Phenomenon.DEPENDENCY]:
            for value in AnnotationService.phenomenon_map[Phenomenon.DEPENDENCY][key]:
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
            if not link.udep_deprel or not dep_to_enum_dict.get(link.udep_deprel):
                continue
            dep: Dependency = dep_to_enum_dict[link.udep_deprel]
            base_node: NodeMC = graph_data.nodes[id_to_node_dict[link.source]]
            FrequencyService.add_frequency_item(base_node, dep, values_to_fi_dict, 1)
            for other_link in id_to_source_link_dict.get(link.target, []):
                if not dep_to_enum_dict.get(other_link.udep_deprel):
                    continue
                base_node = graph_data.nodes[id_to_node_dict[other_link.target]]
                FrequencyService.add_frequency_item(base_node, dep, values_to_fi_dict, 0)
                FrequencyService.increase_frequency_count(
                    [dep.name, dep_to_enum_dict[other_link.udep_deprel].name],
                    [Phenomenon.DEPENDENCY, Phenomenon.DEPENDENCY], values_to_fi_dict)
        for fi in values_to_fi_dict.values():
            fa.append(fi)

    @staticmethod
    def add_frequency_item(base_node: NodeMC, dep: Dependency, values_to_fi_dict: Dict[str, FrequencyItem],
                           target_index: int):
        """ Builds a collection of frequency items for given dependency links. """
        values_list: List[List[str]] = [[base_node.udep_feats], [base_node.udep_lemma], [base_node.udep_upostag]]
        phenomena_list: List[List[Phenomenon]] = [[Phenomenon.FEATS], [Phenomenon.LEMMA], [Phenomenon.UPOSTAG]]
        for vl in values_list:
            vl.insert(target_index, dep.name)
        for pl in phenomena_list:
            pl.insert(target_index, Phenomenon.DEPENDENCY)
        if not base_node.udep_feats or Phenomenon.FEATS not in base_node.udep_feats.lower():
            values_list.pop(0)
            phenomena_list.pop(0)
        for i in range(len(values_list)):
            FrequencyService.increase_frequency_count(values_list[i], phenomena_list[i], values_to_fi_dict)

    @staticmethod
    def add_generic_frequencies(urn: str, search_phenomena: List[Phenomenon]) -> List[FrequencyItem]:
        """ Adds frequency information for case and lemma annotations in a corpus. """
        aql: str = f"{search_phenomena[0]} {Config.AQL_DEP} "
        definition: str = f"1:{search_phenomena[0]},2:"
        fa: List[FrequencyItem] = []
        if search_phenomena[1] == Phenomenon.FEATS:
            aql += f"{Phenomenon.FEATS}={Config.AQL_CASE}"
            definition += Phenomenon.FEATS
            result: List[FrequencyTableEntry] = Config.CORPUS_STORAGE_MANAGER.frequency(
                corpus_name=urn, query=aql, definition=definition)
            fa += [FrequencyItem(x.count, search_phenomena, x.values) for x in result]
        else:
            aql += search_phenomena[1]
            definition += search_phenomena[1]
            result: List[FrequencyTableEntry] = Config.CORPUS_STORAGE_MANAGER.frequency(
                corpus_name=urn, query=aql, definition=definition)
            fa += [FrequencyItem(x.count, search_phenomena, x.values) for x in result]
        return fa

    @staticmethod
    def extract_case_values(fa: List[FrequencyItem]) -> List[FrequencyItem]:
        """ Checks if features were involved in the search and, if yes, extracts the case values from them. """
        values_to_fi_dict: Dict[str, List[FrequencyItem]] = {}
        for fi in fa:
            target_indices: List[int] = [i for i in range(len(fi.phenomena)) if
                                         fi.phenomena[i] == Phenomenon.FEATS]
            for ti in target_indices:
                value_parts: List[str] = fi.values[ti].split("|")
                case_string: str = next(x for x in value_parts if Feats.Case.value in x.lower())
                fi.values[ti] = case_string.split("=")[1]
            values_combined: str = "".join(fi.values)
            values_to_fi_dict[values_combined] = values_to_fi_dict.get(values_combined, []) + [fi]
        ret_val: List[FrequencyItem] = []
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
