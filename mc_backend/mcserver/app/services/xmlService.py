import json
from typing import List, Tuple

from conllu import TokenList
from lxml import etree, objectify
from lxml.etree import _ElementUnicodeResult
from collections import OrderedDict

from mcserver.app.models import ExerciseType, FileType, Solution
from mcserver.app.services import TextService
from mcserver.models_auto import Exercise


class XMLservice:
    """Service for handling XML data."""

    cloze_solution_template: str = \
        "       <dragbox>" \
        "           <text>{0}</text>" \
        "           <group>{1}</group>" \
        "       </dragbox>"

    matching_solution_template: str = \
        "    <subquestion format=\"html\">" \
        "      <text><![CDATA[<p>{0}</p>]]></text>" \
        "      <answer>" \
        "        <text>{1}</text>" \
        "      </answer>" \
        "    </subquestion>"

    tag_template: str = \
        "<tag>" \
        "   <text>{0}</text>" \
        "</tag>"

    quiz_template: str = \
        "<quiz>" \
        "   <question type=\"{0}\">" \
        "       <name>" \
        "           <text>{1}</text>" \
        "       </name>" \
        "       <questiontext format=\"html\">" \
        "           <text><![CDATA[<br><p>{2}</p><p>{3}</p><br><br>]]></text>" \
        "       </questiontext>" \
        "       <generalfeedback format=\"html\">" \
        "           <text>{4}</text>" \
        "       </generalfeedback>" \
        "       <defaultgrade>1.0000000</defaultgrade>" \
        "       <penalty>0.1000000</penalty>" \
        "       <hidden>0</hidden>" \
        "       <shuffleanswers>1</shuffleanswers>" \
        "       <correctfeedback format=\"html\">" \
        "           <text>{5}</text>" \
        "       </correctfeedback>" \
        "       <partiallycorrectfeedback format=\"html\">" \
        "           <text>{6}</text>" \
        "       </partiallycorrectfeedback>" \
        "       <incorrectfeedback format=\"html\">" \
        "           <text>{7}</text>" \
        "       </incorrectfeedback>" \
        "       <shownumcorrect/>" \
        "       {8}" \
        "       <tags>{9}</tags>" \
        "   </question>" \
        "</quiz>"

    @staticmethod
    def create_xml_string(e: Exercise, conll: List[TokenList], file_type: FileType, solutions: List[Solution]) -> str:
        """Exports the exercise data to the Moodle XML format. See https://docs.moodle.org/35/en/Moodle_XML_format ."""
        # fill the main template with metadata (including the actual text)
        if e.exercise_type == ExerciseType.cloze.value:
            text_with_gaps: str = XMLservice.get_moodle_cloze_text_with_solutions(conll, file_type, solutions)
            # fill a template using the node position and solution value, then append it to the other solutions
            quiz_solutions: str = "".join(
                [XMLservice.cloze_solution_template.format(x.target.content, 1) for x in solutions])
            tags: List[str] = [XMLservice.tag_template.format(e.work_author),
                               XMLservice.tag_template.format(e.work_title)] + [XMLservice.tag_template.format(x) for x
                                                                                in json.loads(e.search_values)]
            return XMLservice.quiz_template.format(e.exercise_type, e.exercise_type_translation, e.instructions,
                                                   text_with_gaps, e.general_feedback, e.correct_feedback,
                                                   e.partially_correct_feedback, e.incorrect_feedback, quiz_solutions,
                                                   "".join(tags))
        elif e.exercise_type == ExerciseType.matching.value:
            # fill a template using the node position and solution value, then append it to the other solutions
            quiz_solutions: str = "".join(
                [XMLservice.matching_solution_template.format(x.target.content, x.value.content) for x in solutions])
            return XMLservice.quiz_template.format(e.exercise_type, e.exercise_type_translation, e.instructions, "",
                                                   e.general_feedback, e.correct_feedback, e.partially_correct_feedback,
                                                   e.incorrect_feedback, quiz_solutions, "")

    @staticmethod
    def get_moodle_cloze_text_with_solutions(conll: List[TokenList], file_type: FileType,
                                             solutions: List[Solution]) -> str:
        """Shuffles solutions and adds real gaps to the text."""
        max_gap_length: int = max([len(solution.target.content) for solution in solutions], default=1)
        gap_counter: int = 0
        for solution in solutions:
            gap_counter += 1
            target_token: OrderedDict = TextService.get_token_by_salt_id(solution.target.salt_id, conll)
            target_token["form"] = "[[{0}]]".format(gap_counter) if file_type == FileType.xml else "_" * max_gap_length
        return TextService.strip_whitespace(" ".join([y["form"] for x in conll for y in x]))

    @staticmethod
    def get_text_parts_by_urn(cts_urn_raw: str, xml: etree._Element) -> List[Tuple[str, str]]:
        """ Parses an XML file for the various text parts and maps them to their respective URN. """
        text_list: List[Tuple[str, str]] = []
        base_urn: str = ":".join(cts_urn_raw.split(":")[:-1])
        target_elements_string: str = "*[@n]"
        level1_parts: List[etree._Element] = xml.xpath(
            f"/GetPassage/reply/passage/TEI/text/body/div/{target_elements_string}")
        for l1p in level1_parts:
            level2_parts: List[etree._Element] = l1p.xpath(f"./{target_elements_string}")
            l1p_value: _ElementUnicodeResult = l1p.xpath("@n")[0]
            if level2_parts:
                for l2p in level2_parts:
                    l2p_value: _ElementUnicodeResult = l2p.xpath("@n")[0]
                    level3_parts: List[etree._Element] = l2p.xpath(f"./{target_elements_string}")
                    if level3_parts:
                        for l3p in level3_parts:
                            l3p_value: _ElementUnicodeResult = l3p.xpath("@n")[0]
                            text_values: List[str] = l3p.xpath(".//text()")
                            urn: str = f"{base_urn}:{str(l1p_value)}.{str(l2p_value)}.{str(l3p_value)}"
                            text_list.append((urn, " ".join(" ".join(text_values).split())))
                    else:
                        text_values: List[str] = l2p.xpath(".//text()")
                        urn: str = f"{base_urn}:{str(l1p_value)}.{str(l2p_value)}"
                        text_list.append((urn, " ".join(" ".join(text_values).split())))
            else:
                text_values: List[str] = l1p.xpath(".//text()")
                urn: str = f"{base_urn}:{str(l1p_value)}"
                text_list.append((urn, " ".join(" ".join(text_values).split())))
        return text_list

    @staticmethod
    def strip_name_spaces(xml: etree._Element) -> None:
        """Removes all namespaces from an XML document for easier parsing, e.g. with XPath."""
        # strip namespaces to facilitate searching
        for elem in xml.getiterator():
            if not hasattr(elem.tag, 'find'):
                continue
            i = elem.tag.find('}')
            if i >= 0:
                elem.tag = elem.tag[i + 1:]
        objectify.deannotate(xml, cleanup_namespaces=True)
