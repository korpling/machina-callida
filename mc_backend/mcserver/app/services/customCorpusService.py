import ntpath
import os
from collections import OrderedDict
from typing import List, Tuple, Set, Dict

import conllu
import rapidjson as json
from conllu import TokenList
from flask_restful import abort

from mcserver import Config
from mcserver.app.models import CustomCorpus, Corpus, CitationLevel, TextPart, Citation
from mcserver.app.services import AnnotationService, FileService


class CustomCorpusService:
    """ Service for handling access to custom corpora. Performs CRUD-like operations on the database. """
    custom_corpora: List[CustomCorpus] = [
        CustomCorpus(corpus=Corpus(title="Commentarii de bello Gallico",
                                   source_urn=Config.CUSTOM_CORPUS_PROIEL_URN_TEMPLATE.format("caes-gal"),
                                   author="C. Iulius Caesar",
                                   citation_level_1=CitationLevel.book,
                                   citation_level_2=CitationLevel.chapter,
                                   citation_level_3=CitationLevel.section),
                     file_path=Config.CUSTOM_CORPUS_CAES_GAL_FILE_PATH),
        CustomCorpus(corpus=Corpus(title="Epistulae ad Atticum",
                                   source_urn=Config.CUSTOM_CORPUS_PROIEL_URN_TEMPLATE.format("cic-att"),
                                   author="M. Tullius Cicero",
                                   citation_level_1=CitationLevel.book,
                                   citation_level_2=CitationLevel.letter,
                                   citation_level_3=CitationLevel.section),
                     file_path=Config.CUSTOM_CORPUS_CIC_ATT_FILE_PATH),
        CustomCorpus(corpus=Corpus(title="De officiis",
                                   source_urn=Config.CUSTOM_CORPUS_PROIEL_URN_TEMPLATE.format("cic-off"),
                                   author="M. Tullius Cicero",
                                   citation_level_1=CitationLevel.book,
                                   citation_level_2=CitationLevel.section,
                                   citation_level_3=CitationLevel.default),
                     file_path=Config.CUSTOM_CORPUS_CIC_OFF_FILE_PATH),
        CustomCorpus(corpus=Corpus(title="Vulgata (Novum Testamentum)",
                                   source_urn=Config.CUSTOM_CORPUS_PROIEL_URN_TEMPLATE.format("latin-nt"),
                                   author="Hieronymus",
                                   citation_level_1=CitationLevel.chapter,
                                   citation_level_2=CitationLevel.section,
                                   citation_level_3=CitationLevel.default),
                     file_path=Config.CUSTOM_CORPUS_LATIN_NT_FILE_PATH),
        CustomCorpus(corpus=Corpus(title="Opus Agriculturae",
                                   source_urn=Config.CUSTOM_CORPUS_PROIEL_URN_TEMPLATE.format("pal-agr"),
                                   author="Palladius",
                                   citation_level_1=CitationLevel.book,
                                   citation_level_2=CitationLevel.chapter,
                                   citation_level_3=CitationLevel.section),
                     file_path=Config.CUSTOM_CORPUS_PAL_AGR_FILE_PATH),
        CustomCorpus(corpus=Corpus(title="Peregrinatio Aetheriae",
                                   source_urn=Config.CUSTOM_CORPUS_PROIEL_URN_TEMPLATE.format("per-aeth"),
                                   author="Peregrinatio Aetheriae",
                                   citation_level_1=CitationLevel.chapter,
                                   citation_level_2=CitationLevel.section,
                                   citation_level_3=CitationLevel.default),
                     file_path=Config.CUSTOM_CORPUS_PER_AET_FILE_PATH),
        CustomCorpus(corpus=Corpus(title="VIVA",
                                   source_urn=Config.CUSTOM_CORPUS_VIVA_URN,
                                   author="VIVA (textbook)",
                                   citation_level_1=CitationLevel.book,
                                   citation_level_2=CitationLevel.unit,
                                   citation_level_3=CitationLevel.default),
                     file_path=Config.CUSTOM_CORPUS_VIVA_FILE_PATH)]
    makra_map: Dict[str, str] = {"ā": "a", "Ā": "A", "ē": "e", "Ē": "E", "ō": "o", "Ō": "O", "ī": "i", "Ī": "i",
                                 "ū": "u"}
    punctuation_extended_rare: str = "≫≪–›‹»«…"
    viva_stop_words: Set[str] = {"Während", "Bekanntschaft"}

    @staticmethod
    def extract_custom_corpus_text(relevant_text_parts: List[TextPart], start_parts: List[str], end_parts: List[str],
                                   base_urn: str, current_idx: int = 0, consider_start: List[bool] = None) \
            -> List[Tuple[str, str]]:
        """ Extracts text from the relevant parts of a (custom) corpus. """
        text_list: List[Tuple[str, str]] = []
        nxt: callable = CustomCorpusService.extract_custom_corpus_text_next_level
        for rtp in relevant_text_parts:
            new_urn: str = ("." if current_idx else ":").join([base_urn, str(rtp.citation.value)])
            if current_idx == 0:
                CustomCorpusService.prepare_custom_corpus_text_next_level(rtp, start_parts, end_parts, new_urn,
                                                                          text_list, nxt, current_idx)
            else:
                if consider_start is None:
                    nxt(rtp, start_parts, end_parts, new_urn, text_list, current_idx, None)
                else:
                    if consider_start[0] and rtp.citation.value < int(start_parts[current_idx]):
                        continue
                    elif consider_start[1] and rtp.citation.value > int(end_parts[current_idx]):
                        continue
                    else:
                        CustomCorpusService.prepare_custom_corpus_text_next_level(rtp, start_parts, end_parts, new_urn,
                                                                                  text_list, nxt, current_idx)
        return text_list

    @staticmethod
    def extract_custom_corpus_text_next_level(rtp: TextPart, start_parts: List[str], end_parts: List[str], new_urn: str,
                                              text_list: List[Tuple[str, str]], current_idx: int = 0,
                                              consider_start: List[bool] = None) -> None:
        """ Extracts text from the next level of relevant text parts for a (custom corpus). """
        if current_idx == len(start_parts) - 1:
            text_list.append((new_urn, rtp.text_value))
        else:
            current_idx += 1
            text_list += CustomCorpusService.extract_custom_corpus_text(rtp.sub_text_parts, start_parts,
                                                                        end_parts, new_urn, current_idx, consider_start)

    @staticmethod
    def get_custom_corpus_annotations(urn: str) -> List[TokenList]:
        """ Retrieves the annotated text for a custom non-PROIEL corpus, e.g. a textbook. """
        urn_split: List[str] = []
        if AnnotationService.has_urn_sentence_range(urn):
            urn_split = urn.split("@")
            urn = urn_split[0]
        text_list: List[Tuple[str, str]] = CustomCorpusService.get_custom_corpus_text(urn)
        annotations_conll: str = AnnotationService.get_udpipe(" ".join(x[1] for x in text_list))
        conll: List[TokenList] = AnnotationService.parse_conll_string(annotations_conll)
        if len(urn_split):
            sentence_range: List[int] = list(map(lambda x: int(x), urn_split[1].split("-")))
            ids_to_delete: Set[int] = set()
            for sent in conll:
                sentence_id: int = int(sent.metadata["sent_id"])
                if not sentence_range[0] <= sentence_id <= sentence_range[1]:
                    ids_to_delete.add(sentence_id)
            conll = [x for x in conll if int(x.metadata["sent_id"]) not in ids_to_delete]
            # adjust sentence numbers
            for i in range(len(conll)):
                conll[i].metadata["sent_id"] = str(i + 1)
        return conll

    @staticmethod
    def get_custom_corpus_reff(cts_urn: str) -> List[str]:
        """ Processes requests for references to a custom corpus. """
        disk_urn: str = AnnotationService.get_disk_urn(cts_urn)
        disk_reff: List[str] = FileService.get_reff_from_disk(disk_urn)
        if disk_reff:
            return disk_reff
        target_corpus: CustomCorpus = next(
            (x for x in CustomCorpusService.custom_corpora if x.corpus.source_urn in cts_urn), None)
        if not target_corpus:
            return []
        elif not target_corpus.text_parts:
            target_corpus = CustomCorpusService.init_custom_corpus(target_corpus)
        if cts_urn == target_corpus.corpus.source_urn:
            disk_reff = [(":".join([cts_urn, str(x.citation.value)])) for x in target_corpus.text_parts]
        else:
            disk_reff = CustomCorpusService.get_custom_corpus_sub_reff(cts_urn, target_corpus)
        with open(os.path.join(Config.REFF_CACHE_DIRECTORY, disk_urn), "w+") as f:
            f.write(json.dumps(disk_reff))
        return disk_reff

    @staticmethod
    def get_custom_corpus_sub_reff(cts_urn: str, target_corpus: CustomCorpus) -> List[str]:
        """ Processes requests for nested references to a custom corpus. """
        urn_parts: List[str] = cts_urn.split(":")
        citation_parts: List[int] = []
        try:
            citation_parts = [int(x) for x in urn_parts[-1].split(".")]
        except ValueError:
            abort(400)
        target_text_parts: List[TextPart] = target_corpus.text_parts
        if len(citation_parts) > 1:
            target_text_parts = next(
                x for x in target_corpus.text_parts if x.citation.value == citation_parts[0]).sub_text_parts
        possible_values: Set[int] = set([x.citation.value for x in target_text_parts])
        if citation_parts[-1] in possible_values:
            relevant_text_part: TextPart = next(
                tp for tp in target_text_parts if tp.citation.value == citation_parts[-1])
            return [(".".join([cts_urn, str(x.citation.value)])) for x in relevant_text_part.sub_text_parts]
        else:
            return []

    @staticmethod
    def get_custom_corpus_text(urn: str) -> List[Tuple[str, str]]:
        """ Retrieves the text for a custom corpus, e.g. a textbook. """
        urn_parts: List[str] = urn.split(":")
        base_urn: str = urn.replace(":" + urn_parts[-1], "")
        target_corpus: CustomCorpus = next(
            (x for x in CustomCorpusService.custom_corpora if x.corpus.source_urn == base_urn), None)
        if not target_corpus:
            return []
        last_urn_part: str = urn_parts[-1]
        start_end_split: List[str] = last_urn_part.split("-")
        # we need a text range
        start: str = start_end_split[0]
        end: str = start_end_split[1]
        # choose starting point
        start_parts: List[str] = start.split(".")
        end_parts: List[str] = end.split(".")
        relevant_text_parts: List[TextPart] = [x for x in target_corpus.text_parts if
                                               int(start_parts[0]) <= x.citation.value <= int(end_parts[0])]
        return CustomCorpusService.extract_custom_corpus_text(relevant_text_parts, start_parts, end_parts, base_urn)

    @staticmethod
    def get_treebank_annotations(urn: str) -> List[TokenList]:
        """ Retrieves annotations from a treebank. """
        cc: CustomCorpus = next(x for x in CustomCorpusService.custom_corpora if x.corpus.source_urn in urn)
        annotations: List[TokenList] = []
        file_name: str = ntpath.basename(cc.file_path)
        cache_file_path: str = os.path.join(Config.TREEBANKS_CACHE_DIRECTORY, file_name + ".json")
        if os.path.exists(cache_file_path):
            try:
                annotations = [TokenList(tokens=x["tokens"], metadata=x["metadata"]) for x in
                               json.loads(FileService.get_file_content(cache_file_path))]
            except ValueError:
                pass
        if not annotations:
            annotations = conllu.parse(FileService.get_file_content(cc.file_path))
            # need to cache the result because the syntax parser is so slow
            with open(cache_file_path, "w+") as f:
                f.write(json.dumps(dict(tokens=x.tokens, metadata=x.metadata) for x in annotations))
        if cc.corpus.source_urn != urn:
            # the given URN points to a sub-graph, so we make a selection from our annotations
            annotations = CustomCorpusService.get_treebank_sub_annotations(urn, annotations, cc)
        # add an artificial punctuation sign at the end of each sentence
        for sent in annotations:
            sent.metadata["urn"] = ":".join(urn.split(":")[:-1] + [sent.tokens[0]["misc"]["ref"]])
            if sent.tokens[-1]["form"] != ".":
                root_token: OrderedDict = next(x for x in sent.tokens if x[Config.AQL_DEPREL] == "root")
                sent.append(OrderedDict(
                    [("id", sent.tokens[-1]["id"] + 1), ("form", "."), ("lemma", "."), ("upostag", "PUNCT"),
                     ("xpostag", None), ("feats", None), ("head", root_token["id"] if root_token else 0),
                     ("deps", None), ("misc", OrderedDict([("ref", sent.tokens[0]["misc"]["ref"])]))]))
        # add root dependencies as separate node annotations so we can search for them later
        for token_list in annotations:
            for token in token_list:
                if token["head"] == 0:
                    token["deps"] = token[Config.AQL_DEPREL]
        return annotations

    @staticmethod
    def get_treebank_sub_annotations(urn: str, annotations: List[TokenList], cc: CustomCorpus) -> List[TokenList]:
        """ Retrieves annotations for nested parts of a treebank. """
        target_citation_range: List[str] = urn.split(":")[-1].split("@")
        if len(target_citation_range) > 1:
            # select sentences by ID
            sentence_ids: List[str] = target_citation_range[1].split("-")
            sentence_is_relevant: bool = False
            new_annotations: List[TokenList] = []
            for i in range(len(annotations)):
                if annotations[i].metadata["sent_id"] == sentence_ids[0]:
                    sentence_is_relevant = True
                if sentence_is_relevant:
                    new_annotations.append(annotations[i])
                if annotations[i].metadata["sent_id"] == sentence_ids[1]:
                    break
            return new_annotations
        else:
            if not cc.text_parts:
                cc = CustomCorpusService.init_custom_corpus(cc)
            # just regular CTS citation, need to get the correct labels
            target_citation_range = target_citation_range[0].split("-")
            start_citation_label: str = AnnotationService.get_citation_label(
                cc.text_parts, [int(x) for x in target_citation_range[0].split(".")])
            end_citation_label: str = AnnotationService.get_citation_label(
                cc.text_parts, [int(x) for x in target_citation_range[1].split(".")])
            start_index: int = -1
            end_index: int = -1
            for i in range(len(annotations)):
                if start_index < 0 and annotations[i].tokens[0]["misc"]["ref"] == start_citation_label:
                    start_index = i
                if start_index >= 0 and annotations[i].tokens[0]["misc"]["ref"] == end_citation_label and \
                        (i == len(annotations) - 1 or
                         annotations[i + 1].tokens[0]["misc"]["ref"] != end_citation_label):
                    end_index = i
                    break
            return annotations[start_index: (end_index + 1)]

    @staticmethod
    def init_custom_corpus(cc: CustomCorpus) -> CustomCorpus:
        """Adds custom corpora to the corpus list, e.g. the PROIEL corpora."""
        # skip VIVA because we do it separately
        if cc.corpus.source_urn == Config.CUSTOM_CORPUS_VIVA_URN:
            CustomCorpusService.init_custom_corpus_viva()
            return cc
        annotations: List[TokenList] = CustomCorpusService.get_treebank_annotations(cc.corpus.source_urn)
        for sent in annotations:
            citation_ref: str = sent.tokens[0]["misc"]["ref"]
            citation_parts: List[str] = citation_ref.split(".")
            if len(cc.text_parts) == 0 or cc.text_parts[-1].citation.label != citation_parts[0]:
                cc.text_parts.append(
                    TextPart(citation=Citation(level=CitationLevel[cc.corpus.citation_level_1.lower()],
                                               label=citation_parts[0], value=len(cc.text_parts) + 1)))
            target_text_parts: List[TextPart] = cc.text_parts[-1].sub_text_parts
            if cc.corpus.citation_level_2 != CitationLevel.default.value and (
                    len(target_text_parts) == 0 or target_text_parts[-1].citation.label != citation_parts[1]):
                target_text_parts.append(
                    TextPart(citation=Citation(level=CitationLevel[cc.corpus.citation_level_2.lower()],
                                               label=citation_parts[1], value=len(target_text_parts) + 1)))
            target_text_parts = cc.text_parts[-1].sub_text_parts[-1].sub_text_parts
            if cc.corpus.citation_level_3 != CitationLevel.default.value:
                if len(citation_parts) < 3:
                    citation_parts.append("1")
                if len(target_text_parts) == 0 or target_text_parts[-1].citation.label != citation_parts[2]:
                    target_text_parts.append(
                        TextPart(citation=Citation(level=CitationLevel[cc.corpus.citation_level_3.lower()],
                                                   label=citation_parts[2], value=len(target_text_parts) + 1)))
            target_text_part: TextPart = cc.text_parts[
                -1] if cc.corpus.citation_level_2 == CitationLevel.default.value else (
                cc.text_parts[-1].sub_text_parts[
                    -1] if cc.corpus.citation_level_3 == CitationLevel.default.value else
                cc.text_parts[-1].sub_text_parts[-1].sub_text_parts[-1])
            target_text_part.text_value += " ".join(x["form"] for x in sent.tokens)
        return cc

    @staticmethod
    def init_custom_corpus_viva():
        """ Initializes the citation system for the VIVA textbook. """
        previous_line = ""
        viva_custom_corpus: CustomCorpus = next(
            x for x in CustomCorpusService.custom_corpora if x.corpus.source_urn == Config.CUSTOM_CORPUS_VIVA_URN)
        is_processing_unit_text: bool = False
        unit_count: int = 0
        text_part_count: int = 0
        with open(viva_custom_corpus.file_path, "r", encoding="utf-8") as vivaFile:
            for line in vivaFile:
                # check if line is empty
                if not line.strip():
                    continue
                # check if line starts with a number or contains stop words
                if line[0].isdigit():
                    is_processing_unit_text = False
                elif not any(x in line for x in CustomCorpusService.viva_stop_words):
                    if "Lektion " in line:
                        unit_count += 1
                        text_part_count += 1
                        viva_custom_corpus.text_parts[-1].sub_text_parts.append(
                            TextPart(citation=Citation(level=CitationLevel.unit, label=str(unit_count),
                                                       value=text_part_count)))
                    elif line.startswith("Zusatztext") or line.startswith("*"):
                        text_part_count += 1
                        viva_custom_corpus.text_parts[-1].sub_text_parts.append(
                            TextPart(citation=Citation(level=CitationLevel.unit, label=str(unit_count) + "Z",
                                                       value=text_part_count)))
                    elif "Lektionstexte" in line:
                        book_count: int = len(viva_custom_corpus.text_parts) + 1
                        viva_custom_corpus.text_parts.append(
                            TextPart(
                                citation=Citation(level=CitationLevel.book, label=str(book_count), value=book_count)))
                    else:
                        if not (previous_line[0].isdigit() or is_processing_unit_text):
                            continue
                        is_processing_unit_text = True
                        for per in CustomCorpusService.punctuation_extended_rare:
                            line = line.replace(per, "")
                        for makron in CustomCorpusService.makra_map:
                            line = line.replace(makron, CustomCorpusService.makra_map[makron])
                        line = "".join([char for char in line.replace("\n", "") if not char.isdigit()])
                        if viva_custom_corpus.text_parts[-1].sub_text_parts[-1].text_value and \
                                viva_custom_corpus.text_parts[-1].sub_text_parts[-1].text_value[-1] != " ":
                            viva_custom_corpus.text_parts[-1].sub_text_parts[-1].text_value += " "
                        # remove duplicate/multiple whitespaces in a row
                        line = " ".join(line.split())
                        viva_custom_corpus.text_parts[-1].sub_text_parts[-1].text_value += line
                previous_line = line

    @staticmethod
    def is_custom_corpus_proiel(urn: str):
        """ Checks whether a given URN belongs to a custom corpus from the PROIEL treebank. """
        return "proiel" in urn

    @staticmethod
    def is_custom_corpus_urn(urn: str):
        """ Checks whether a given URN belongs to a custom corpus or a standard/CTS corpus. """
        return "custom" in urn

    @staticmethod
    def prepare_custom_corpus_text_next_level(rtp: TextPart, start_parts: List[str], end_parts: List[str], new_urn: str,
                                              text_list: List[Tuple[str, str]], nxt: callable,
                                              current_idx: int = 0) -> None:
        """ Identifies possible candidates and relevant URN parts for the next text level. """
        if int(start_parts[current_idx]) < rtp.citation.value < int(end_parts[current_idx]):
            nxt(rtp, start_parts, end_parts, new_urn, text_list, current_idx, None)
        else:
            consider_start = [int(start_parts[current_idx]) == rtp.citation.value,
                              int(end_parts[current_idx]) == rtp.citation.value]
            nxt(rtp, start_parts, end_parts, new_urn, text_list, current_idx, consider_start)
