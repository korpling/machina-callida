import json
import os
import re
import string
import sys
from collections import OrderedDict
from typing import Dict, Set, List

import conllu
import requests
from conllu import TokenList

from mcserver.app.models import Exercise, Solution
from mcserver.config import Config


class TextService:
    """ Service for manipulating texts / strings. """

    orthography_map: Dict[str, str] = {"que": "", "u": "v", "U": "V", "v": "u", "V": "U"}
    proper_nouns_set: Set[str]
    sentence_count_ranges: List[range] = [range(0, 2), range(2, 5), range(5, 10), range(10, 20), range(20, 40),
                                          range(40, 70), range(70, 110), range(110, 160), range(160, sys.maxsize)]
    stop_words_latin: Set[str] = set()
    suffix_map: Dict[str, Set[str]] = {"e": {"is", "us"}, "um": {"us"}, "us": {"i"}}
    word_count_ranges: List[range] = [range(0, 10), range(10, 50), range(50, 100), range(100, 250), range(250, 500),
                                      range(500, 1000), range(1000, 1500), range(1500, 2000), range(2000, sys.maxsize)]

    @staticmethod
    def get_h5p_text_with_solutions(exercise: Exercise, solution_indices: List[int]) -> str:
        """ Builds a string to be used in the textfield property value of a content.json file for H5P
        drag the words exercises. """
        solutions: List[Solution] = TextService.get_solutions_by_index(exercise, solution_indices)
        conll: List[TokenList] = conllu.parse(exercise.conll)
        for solution in solutions:
            target_token: OrderedDict = TextService.get_token_by_salt_id(solution.target.salt_id, conll)
            target_token["form"] = "*{0}*".format(target_token["form"])
        text_with_gaps: str = TextService.strip_whitespace(" ".join([y["form"] for x in conll for y in x]))
        return text_with_gaps

    @staticmethod
    def get_solutions_by_index(exercise: Exercise, solution_indices: List[int] = None) -> List[Solution]:
        """ If available, makes use of the solution indices to return only the wanted solutions. """
        available_solutions: List[Solution] = [Solution(json_dict=x) for x in json.loads(exercise.solutions)]
        if solution_indices is None:
            return available_solutions
        return [available_solutions[i] for i in solution_indices] if len(solution_indices) > 0 else []

    @staticmethod
    def get_token_by_salt_id(salt_id: str, conll: List[TokenList]):
        """Searches textual data for a specific token, given its SALT ID."""
        key_parts: List[str] = salt_id.split("#")[-1].split("tok")
        sentence_id: str = key_parts[0].replace("sent", "")
        target_sentence: TokenList = next(x for x in conll if x.metadata["sent_id"] == sentence_id)
        token_id: str = key_parts[1]
        return next(x for x in target_sentence if x["id"] == int(token_id))

    @staticmethod
    def init_proper_nouns_list() -> None:
        """Reads from the proper nouns file and it stores it in the TextServices."""
        from mcserver.app.services import FileService
        TextService.proper_nouns_set = set(FileService.get_file_content(
            os.path.join(Config.ASSETS_DIRECTORY, 'proper_nouns.txt')).split('\n'))

    @staticmethod
    def init_stop_words_latin() -> None:
        """Initializes the stop words list for Latin texts and caches it if necessary."""
        content: str
        if os.path.exists(Config.STOP_WORDS_LATIN_PATH):
            with open(Config.STOP_WORDS_LATIN_PATH, encoding="utf-8") as stop_words_file:
                content = stop_words_file.read()
        else:
            response: requests.Response = requests.get(Config.STOP_WORDS_URL)
            content = response.text
            with open(Config.STOP_WORDS_LATIN_PATH, "w+", encoding="utf-8") as stop_words_file:
                stop_words_file.write(content)
        stop_words_dict: Dict[str, List[str]] = json.loads(content)
        TextService.stop_words_latin = set(y for x in stop_words_dict.values() for y in x)

    @staticmethod
    def strip_whitespace(text: str) -> str:
        """ Removes extra whitespace before punctuation signs, but leaves it for underscores / word gaps. """
        return re.sub('[ ]([{0}])'.format(string.punctuation.replace("_", "").replace("*", "")), r'\1', text.strip())
