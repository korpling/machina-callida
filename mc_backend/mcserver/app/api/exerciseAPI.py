import uuid
from datetime import datetime
import connexion
import rapidjson as json
from typing import List, Dict, Union
import requests
from connexion.lifecycle import ConnexionResponse
from flask import Response
from mcserver.app import db
from mcserver.app.models import ExerciseType, Solution, ExerciseData, AnnisResponse, Phenomenon, TextComplexity, \
    TextComplexityMeasure, ResourceType, ExerciseMC
from mcserver.app.services import AnnotationService, CorpusService, NetworkService, TextComplexityService
from mcserver.config import Config
from mcserver.models_auto import Exercise, TExercise, UpdateInfo


def adjust_solutions(exercise_data: ExerciseData, exercise_type: str, solutions: List[Solution]) -> List[Solution]:
    """Adds the content to each SolutionElement."""
    if exercise_type == ExerciseType.matching.value:
        node_id_dict: Dict[str, int] = dict(
            (exercise_data.graph.nodes[i].id, i) for i in range(len(exercise_data.graph.nodes)))
        for solution in solutions:
            solution.target.content = exercise_data.graph.nodes[node_id_dict[solution.target.salt_id]].annis_tok
            solution.value.content = exercise_data.graph.nodes[node_id_dict[solution.value.salt_id]].annis_tok
    return solutions


def get(eid: str) -> Union[Response, ConnexionResponse]:
    exercise: TExercise = db.session.query(Exercise).filter_by(eid=eid).first()
    if exercise is None:
        return connexion.problem(404, Config.ERROR_TITLE_NOT_FOUND, Config.ERROR_MESSAGE_EXERCISE_NOT_FOUND)
    ar: AnnisResponse = CorpusService.get_corpus(cts_urn=exercise.urn, is_csm=False)
    if not ar.nodes:
        return connexion.problem(404, Config.ERROR_TITLE_NOT_FOUND, Config.ERROR_MESSAGE_CORPUS_NOT_FOUND)
    exercise.last_access_time = datetime.utcnow().timestamp()
    db.session.commit()
    exercise_type: ExerciseType = ExerciseType(exercise.exercise_type)
    ar.solutions = json.loads(exercise.solutions)
    ar.uri = NetworkService.get_exercise_uri(exercise)
    ar.exercise_id = exercise.eid
    ar.exercise_type = exercise_type.value
    return NetworkService.make_json_response(ar.__dict__)


def get_graph_data(title: str, conll_string_or_urn: str, aqls: List[str], exercise_type: ExerciseType,
                   search_phenomena: List[Phenomenon]):
    """Sends annotated text data or a URN to the Corpus Storage Manager in order to get a graph."""
    url: str = f"{Config.INTERNET_PROTOCOL}{Config.HOST_IP_CSM}:{Config.CORPUS_STORAGE_MANAGER_PORT}"
    data: str = json.dumps(
        dict(title=title, annotations=conll_string_or_urn, aqls=aqls, exercise_type=exercise_type.name,
             search_phenomena=[x.name for x in search_phenomena]))
    response: requests.Response = requests.post(url, data=data)
    try:
        return json.loads(response.text)
    except ValueError:
        raise


def make_new_exercise(conll: str, correct_feedback: str, exercise_type: str, general_feedback: str,
                      graph_data_raw: dict, incorrect_feedback: str, instructions: str, language: str,
                      partially_correct_feedback: str, search_values: str, solutions: List[Solution],
                      type_translation: str, urn: str, work_author: str, work_title: str) -> AnnisResponse:
    """ Creates a new exercise and makes it JSON serializable. """
    # generate a GUID so we can offer the exercise XML as a file download
    xml_guid = str(uuid.uuid4())
    # assemble the mapped exercise data
    ed: ExerciseData = AnnotationService.map_graph_data_to_exercise(
        graph_data_raw=graph_data_raw, solutions=solutions, xml_guid=xml_guid)
    # for markWords exercises, add the maximum number of correct solutions to the description
    instructions += (f"({len(solutions)})" if exercise_type == ExerciseType.markWords.value else "")
    # map the exercise data to our database data model
    new_exercise: Exercise = map_exercise_data_to_database(
        solutions=solutions, exercise_data=ed, exercise_type=exercise_type, instructions=instructions,
        xml_guid=xml_guid, correct_feedback=correct_feedback, partially_correct_feedback=partially_correct_feedback,
        incorrect_feedback=incorrect_feedback, general_feedback=general_feedback,
        exercise_type_translation=type_translation, conll=conll, work_author=work_author, work_title=work_title,
        search_values=search_values, urn=urn, language=language)
    # create a response
    return AnnisResponse(
        solutions=json.loads(new_exercise.solutions), uri=f"{Config.SERVER_URI_FILE}/{new_exercise.eid}",
        exercise_id=xml_guid)


def map_exercise_data_to_database(exercise_data: ExerciseData, exercise_type: str, instructions: str, xml_guid: str,
                                  correct_feedback: str, partially_correct_feedback: str, incorrect_feedback: str,
                                  general_feedback: str, exercise_type_translation: str, search_values: str,
                                  solutions: List[Solution], conll: str, work_author: str, work_title: str, urn: str,
                                  language: str):
    """Maps the exercise data so we can save it to the database."""
    # sort the nodes according to the ordering links
    AnnotationService.sort_nodes(graph_data=exercise_data.graph)
    # add content to solutions
    solutions: List[Solution] = adjust_solutions(exercise_data=exercise_data, solutions=solutions,
                                                 exercise_type=exercise_type)
    quiz_solutions: str = json.dumps([x.serialize() for x in solutions])
    tc: TextComplexity = TextComplexityService.text_complexity(TextComplexityMeasure.all.name, urn, False,
                                                               exercise_data.graph)
    new_exercise: Exercise = ExerciseMC.from_dict(
        conll=conll, correct_feedback=correct_feedback, eid=xml_guid, exercise_type=exercise_type,
        exercise_type_translation=exercise_type_translation, general_feedback=general_feedback,
        incorrect_feedback=incorrect_feedback, instructions=instructions, language=language,
        last_access_time=datetime.utcnow().timestamp(), partially_correct_feedback=partially_correct_feedback,
        search_values=search_values, solutions=quiz_solutions, text_complexity=tc.all, work_author=work_author,
        work_title=work_title, urn=urn)
    # add the mapped exercise to the database
    db.session.add(new_exercise)
    ui_exercises: UpdateInfo = db.session.query(UpdateInfo).filter_by(
        resource_type=ResourceType.exercise_list.name).first()
    ui_exercises.last_modified_time = datetime.utcnow().timestamp()
    db.session.commit()
    return new_exercise


def post(exercise_data: dict) -> Union[Response, ConnexionResponse]:
    exercise_type: ExerciseType = ExerciseType(exercise_data["type"])
    search_values_list: List[str] = json.loads(exercise_data["search_values"])
    aqls: List[str] = AnnotationService.map_search_values_to_aql(search_values_list=search_values_list,
                                                                 exercise_type=exercise_type)
    search_phenomena: List[Phenomenon] = [Phenomenon[x.split("=")[0]] for x in search_values_list]
    urn: str = exercise_data.get("urn", "")
    # if there is custom text instead of a URN, immediately annotate it
    conll_string_or_urn: str = urn if CorpusService.is_urn(urn) else AnnotationService.get_udpipe(
        CorpusService.get_raw_text(urn, False))
    try:
        # construct graph from CONLL data
        response: dict = get_graph_data(title=urn, conll_string_or_urn=conll_string_or_urn, aqls=aqls,
                                        exercise_type=exercise_type, search_phenomena=search_phenomena)
    except ValueError:
        return connexion.problem(500, Config.ERROR_TITLE_INTERNAL_SERVER_ERROR,
                                 Config.ERROR_MESSAGE_INTERNAL_SERVER_ERROR)
    solutions_dict_list: List[Dict] = response["solutions"]
    solutions: List[Solution] = [Solution(json_dict=x) for x in solutions_dict_list]
    ar: AnnisResponse = make_new_exercise(
        conll=response["conll"], correct_feedback=exercise_data.get("correct_feedback", ""),
        exercise_type=exercise_data["type"], general_feedback=exercise_data.get("general_feedback", ""),
        graph_data_raw=response["graph_data_raw"], incorrect_feedback=exercise_data.get("incorrect_feedback", ""),
        instructions=exercise_data["instructions"], language=exercise_data.get("language", "de"),
        partially_correct_feedback=exercise_data.get("partially_correct_feedback", ""),
        search_values=exercise_data["search_values"], solutions=solutions,
        type_translation=exercise_data.get("type_translation", ""), urn=urn,
        work_author=exercise_data.get("work_author", ""), work_title=exercise_data.get("work_title", ""))
    return NetworkService.make_json_response(ar.__dict__)
