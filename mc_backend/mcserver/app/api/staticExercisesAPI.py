import json
import os
import re
import string
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from io import BytesIO
from tempfile import mkstemp
from time import time
from typing import Dict, List, Set, Match, Tuple, Union
from zipfile import ZipFile

import connexion
import requests
from connexion.lifecycle import ConnexionResponse
from requests import Response

from mcserver.app.models import StaticExercise
from mcserver.app.services import NetworkService, AnnotationService
from mcserver.config import Config
from openapi.openapi_server.models import ExerciseTypePath


def get() -> Union[Response, ConnexionResponse]:
    """ The GET method for the StaticExercises REST API. It provides a list of static exercises
    and their respective URLs in the frontend. """
    # TODO: WRITE AND READ LAST UPDATE TIME FROM THE DATABASE
    if datetime.fromtimestamp(time() - Config.INTERVAL_STATIC_EXERCISES) > NetworkService.exercises_last_update \
            or len(NetworkService.exercises) == 0:
        return update_exercises()
    return NetworkService.make_json_response(
        {x: NetworkService.exercises[x].to_dict() for x in NetworkService.exercises})


def get_relevant_strings(response: Response):
    """ Extracts from the exercises all inflected Latin words that serve as solutions. """
    relevant_strings_dict: Dict[str, Set[str]] = {}
    with ZipFile(BytesIO(response.content)) as zip_file:
        fill_blanks_black_list: Set[str] = {"3", "5", "8", "10"}
        multi_choice_black_list: Set[str] = {"19", "20", "21", "22", "23", "24"}
        files: List[str] = zip_file.namelist()
        for name in [x for x in files if x.endswith(".json") and x.split("/")[-2] == "content"]:
            name_parts: List[str] = name.split("/")
            file_name: str = name_parts[-1].split("_")[0]
            exercise_type: str = name_parts[-3]
            url: str = Config.PUBLIC_FRONTEND_URL + "exercise?type=" + exercise_type + "&file=" + file_name
            content: dict = json.loads(zip_file.read(name).decode("utf-8"))
            if url not in relevant_strings_dict:
                relevant_strings_dict[url] = set()
            if ExerciseTypePath.DRAG_TEXT in name:
                text_field_content: str = content["textField"]
                asterisks: List[int] = [i for i, char in enumerate(text_field_content) if char == "*"]
                for i in range(round(len(asterisks) / 2)):
                    solution_text: str = text_field_content[(asterisks[i * 2] + 1):asterisks[(i * 2) + 1]]
                    for target in solution_text.split(":")[0].strip().split():
                        relevant_strings_dict[url].add(target)
            elif ExerciseTypePath.FILL_BLANKS in name:
                handle_fill_blanks(content, file_name, fill_blanks_black_list, url, relevant_strings_dict)
            elif ExerciseTypePath.MULTI_CHOICE in name and file_name not in multi_choice_black_list:
                handle_multi_choice(content, url, relevant_strings_dict, file_name)
            elif ExerciseTypePath.VOC_LIST in name:
                handle_voc_list(content, url, relevant_strings_dict)
    return relevant_strings_dict


def handle_fill_blanks(content: dict, file_name: str, fill_blanks_black_list: Set[str], url: str,
                       relevant_strings_dict: Dict[str, Set[str]]):
    """ Extracts from a fill_blanks exercises all inflected Latin words that serve as solutions. """
    questions: List[str] = content["questions"]
    for i in range(len(questions)):
        asterisks: List[int] = [i for i, char in enumerate(questions[i]) if char == "*"]
        if file_name in {"1", "6"}:
            asterisks = asterisks[:2]
        elif file_name in {"4"}:
            asterisks = asterisks[:4]
        elif file_name in {"13"} and i == 1:
            asterisks = [k for k, char in enumerate(questions[i]) if char == '"']
        for j in range(round(len(asterisks) / 2)):
            solution_text: str = questions[i][(asterisks[j * 2] + 1):asterisks[(j * 2) + 1]]
            target: str = solution_text.split(":")[0].strip()
            if file_name in fill_blanks_black_list:
                target = questions[i][3:questions[i].find(" ")]
            for word in [y for x in target.split("/") for y in x.split(",")[0].strip().split()]:
                relevant_strings_dict[url].add(word)


def handle_multi_choice(content: dict, url: str, relevant_strings_dict: Dict[str, Set[str]], file_name: str):
    """ Extracts from a multi_choice exercises all inflected Latin words that serve as solutions. """
    question_text: str = content["question"]
    match: Match = re.search(r"<em>(.*)</em>", question_text)
    if not match:
        match = re.search(r"<b>(.*?)</b>", question_text)
        if match and file_name not in {"9", "18"}:
            relevant_strings_dict[url].add(match.group(1))
        else:
            answers: List[dict] = content["answers"]
            correct_answers: List[dict] = [x for x in answers if x["correct"]]
            for answer in correct_answers:
                text: str = answer["text"]
                relevant_strings_dict[url].add(text.replace("<div>", "").replace("</div>", "").strip())
    else:
        match_string: str = match.group(1)
        for solution in match_string.translate(str.maketrans("", "", string.punctuation)).split():
            relevant_strings_dict[url].add(solution)


def handle_voc_list(content: dict, url: str, relevant_strings_dict: Dict[str, Set[str]]):
    """ Extracts from a voc_list exercises all inflected Latin words that serve as solutions. """
    questions: List[str] = content["questions"]
    # don't use round(x) because it will round 0.5 to 0 (>> rounding to nearest even number)
    for i in range(int(Decimal((len(questions) / 2)).quantize(0, ROUND_HALF_UP))):
        match: Match = re.search(r"<h4>(.*)</h4>", questions[i * 2])
        match_string: str = match.group(1)
        match_parts: List[str] = match_string.translate(str.maketrans("", "", string.punctuation)).split()
        relevant_strings_dict[url].add(match_parts[0])


def update_exercises() -> Union[Response, ConnexionResponse]:
    """ Gets all static exercises from the frontend code repository and looks for the lemmata in them."""
    # TODO: check last update of the directory before pulling the whole zip archive
    response: Response = requests.get(Config.STATIC_EXERCISES_REPOSITORY_URL, stream=True)
    if not response.ok:
        return connexion.problem(
            503, Config.ERROR_TITLE_SERVICE_UNAVAILABLE, Config.ERROR_MESSAGE_SERVICE_UNAVAILABLE)
    relevant_strings_dict: Dict[str, Set[str]] = get_relevant_strings(response)
    file_dict: Dict = {}
    lemma_set: Set[str] = set()
    for url in relevant_strings_dict:
        for word in relevant_strings_dict[url]:
            if word not in lemma_set:
                lemma_set.add(word)
                input_bytes = bytearray(word, encoding='utf-8', errors='strict')
                file_handler, file_path = mkstemp()
                os.write(file_handler, input_bytes)
                file_dict[file_path] = file_handler
    result_string: str = AnnotationService.get_udpipe("", False, file_dict)
    search_results: List[Tuple[str, str]] = re.findall(r"1\t([a-zA-Z]*)\t([a-zA-Z]*)", result_string)
    search_results_dict: Dict[str, int] = {item[0]: i for (i, item) in enumerate(search_results)}
    for url in relevant_strings_dict:
        # the URN points to Cicero's letters to his brother Quintus, 1.1.8-1.1.10
        NetworkService.exercises[url] = StaticExercise(
            solutions=[], urn="urn:cts:latinLit:phi0474.phi058.perseus-lat1:1.1.8-1.1.10")
        for word in relevant_strings_dict[url]:
            # UDpipe cannot handle name abbreviations, so remove the punctuation and only keep the upper case letter
            if word[-1] in string.punctuation:
                word = word[:-1]
            NetworkService.exercises[url].solutions.append(list(search_results[search_results_dict[word]]))
    NetworkService.exercises_last_update = datetime.fromtimestamp(time())
    return NetworkService.make_json_response(
        {x: NetworkService.exercises[x].to_dict() for x in NetworkService.exercises})
