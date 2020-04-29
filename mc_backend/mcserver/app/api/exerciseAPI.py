import uuid
from collections import OrderedDict
from datetime import datetime

import rapidjson as json
from typing import List, Dict

import requests
from flask_restful import Resource, reqparse, marshal, abort

from mcserver.app import db
from mcserver.app.models import ExerciseType, Solution, ExerciseData, Exercise, exercise_fields, AnnisResponse, \
    Phenomenon, TextComplexity, TextComplexityMeasure, UpdateInfo, ResourceType
from mcserver.app.services import AnnotationService, CorpusService, NetworkService, TextComplexityService
from mcserver.config import Config


class ExerciseAPI(Resource):
    """The exercise API resource. It creates exercises for a given text."""

    def __init__(self):
        """Initialize possible arguments for calls to the exercise REST API."""
        # TODO: switch to other request parser, e.g. Marshmallow, because the one used by Flask-RESTful does not allow parsing arguments from different locations, e.g. one argument from 'location=args' and another argument from 'location=form'
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("urn", type=str, required=False, location="form", help="No URN provided")
        self.reqparse.add_argument("type", type=str, required=False, location="form", help="No exercise type provided")
        self.reqparse.add_argument("search_values", type=str, required=False, location="form",
                                   help="No search value provided")
        self.reqparse.add_argument("type_translation", type=str, location="form", required=False,
                                   help="No exercise type translation provided")
        self.reqparse.add_argument("work_author", type=str, location="form", required=False,
                                   help="No work_author provided", default="")
        self.reqparse.add_argument("work_title", type=str, required=False, location="form",
                                   help="No work title provided", default="")
        self.reqparse.add_argument("instructions", type=str, required=False, location="form", default="")
        self.reqparse.add_argument("general_feedback", type=str, required=False, location="form", default=" ")
        self.reqparse.add_argument("correct_feedback", type=str, required=False, location="form", default=" ")
        self.reqparse.add_argument("partially_correct_feedback", type=str, required=False, location="form", default=" ")
        self.reqparse.add_argument("incorrect_feedback", type=str, required=False, location="form", default=" ")
        self.reqparse.add_argument("eid", type=str, required=False, location="args", help="No exercise ID provided")
        super(ExerciseAPI, self).__init__()

    def get(self):
        args: dict = self.reqparse.parse_args()
        eid: str = args["eid"]
        exercise: Exercise = Exercise.query.filter_by(eid=eid).first()
        if exercise is None:
            abort(404)
        ar: AnnisResponse = CorpusService.get_corpus(cts_urn=exercise.urn, is_csm=False)
        if not ar.nodes:
            abort(404)
        exercise_type: ExerciseType = ExerciseType(exercise.exercise_type)
        ar.solutions = json.loads(exercise.solutions)
        ar.uri = exercise.uri
        ar.exercise_id = exercise.eid
        ar.exercise_type = exercise_type.value
        return NetworkService.make_json_response(ar.__dict__)

    def post(self):
        # get request arguments
        args: dict = self.reqparse.parse_args()
        urn: str = args["urn"]
        exercise_type: ExerciseType = ExerciseType(args["type"])
        search_values_json: str = args["search_values"]
        search_values_list: List[str] = json.loads(search_values_json)
        aqls: List[str] = AnnotationService.map_search_values_to_aql(search_values_list=search_values_list,
                                                                     exercise_type=exercise_type)
        search_phenomena: List[Phenomenon] = [Phenomenon[x.split("=")[0]] for x in search_values_list]
        # if there is custom text instead of a URN, immediately annotate it
        conll_string_or_urn: str = urn if CorpusService.is_urn(urn) else AnnotationService.get_udpipe(
            CorpusService.get_raw_text(urn, False))
        # construct graph from CONLL data
        response: dict = get_graph_data(title=urn, conll_string_or_urn=conll_string_or_urn, aqls=aqls,
                                        exercise_type=exercise_type, search_phenomena=search_phenomena)
        solutions_dict_list: List[Dict] = response["solutions"]
        solutions: List[Solution] = [Solution(json_dict=x) for x in solutions_dict_list]
        ar: AnnisResponse = make_new_exercise(graph_data_raw=response["graph_data_raw"], solutions=solutions, args=args,
                                              conll=response["conll"], search_values=args["search_values"], urn=urn)
        return NetworkService.make_json_response(ar.__dict__)


def adjust_solutions(exercise_data: ExerciseData, exercise_type: str, solutions: List[Solution]) -> List[Solution]:
    """Adds the content to each SolutionElement."""
    if exercise_type == ExerciseType.matching.value:
        node_id_dict: Dict[str, int] = dict(
            (exercise_data.graph.nodes[i].id, i) for i in range(len(exercise_data.graph.nodes)))
        for solution in solutions:
            solution.target.content = exercise_data.graph.nodes[node_id_dict[solution.target.salt_id]].annis_tok
            solution.value.content = exercise_data.graph.nodes[node_id_dict[solution.value.salt_id]].annis_tok
    return solutions


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
        abort(500)


def make_new_exercise(solutions: List[Solution], args: dict, search_values: str, graph_data_raw: dict,
                      conll: str, urn: str) -> AnnisResponse:
    """ Creates a new exercise and makes it JSON serializable. """
    # generate a GUID so we can offer the exercise XML as a file download
    xml_guid = str(uuid.uuid4())
    # assemble the mapped exercise data
    ed: ExerciseData = AnnotationService.map_graph_data_to_exercise(graph_data_raw=graph_data_raw, solutions=solutions,
                                                                    xml_guid=xml_guid)
    exercise_type = args["type"]
    # for markWords exercises, add the maximum number of correct solutions to the description
    instructions: str = args["instructions"] + (
        f"({len(solutions)})" if exercise_type == ExerciseType.markWords.value else "")
    # map the exercise data to our database data model
    new_exercise: Exercise = map_exercise_data_to_database(solutions=solutions, exercise_data=ed,
                                                           exercise_type=exercise_type, instructions=instructions,
                                                           xml_guid=xml_guid, correct_feedback=args["correct_feedback"],
                                                           partially_correct_feedback=args[
                                                               "partially_correct_feedback"],
                                                           incorrect_feedback=args["incorrect_feedback"],
                                                           general_feedback=args["general_feedback"],
                                                           exercise_type_translation=args.get("type_translation", ""),
                                                           conll=conll, work_author=args["work_author"],
                                                           work_title=args["work_title"], search_values=search_values,
                                                           urn=urn)
    # marshal the whole object so we can get the right URI for download purposes
    new_exercise_marshal: OrderedDict = marshal(new_exercise, exercise_fields)
    # create a response
    return AnnisResponse(solutions=json.loads(new_exercise.solutions), uri=new_exercise_marshal["uri"],
                         exercise_id=xml_guid)


def map_exercise_data_to_database(exercise_data: ExerciseData, exercise_type: str, instructions: str, xml_guid: str,
                                  correct_feedback: str, partially_correct_feedback: str, incorrect_feedback: str,
                                  general_feedback: str, exercise_type_translation: str, search_values: str,
                                  solutions: List[Solution], conll: str, work_author: str, work_title: str, urn: str):
    """Maps the exercise data so we can save it to the database."""
    # sort the nodes according to the ordering links
    AnnotationService.sort_nodes(graph_data=exercise_data.graph)
    # add content to solutions
    solutions = adjust_solutions(exercise_data=exercise_data, solutions=solutions, exercise_type=exercise_type)
    quiz_solutions: str = json.dumps([x.serialize() for x in solutions])
    tc: TextComplexity = TextComplexityService.text_complexity(TextComplexityMeasure.all.name, urn, False,
                                                               exercise_data.graph)
    new_exercise: Exercise = Exercise(conll=conll, correct_feedback=correct_feedback, eid=xml_guid,
                                      exercise_type=exercise_type, exercise_type_translation=exercise_type_translation,
                                      general_feedback=general_feedback, incorrect_feedback=incorrect_feedback,
                                      instructions=instructions, partially_correct_feedback=partially_correct_feedback,
                                      search_values=search_values, solutions=quiz_solutions, text_complexity=tc.all,
                                      work_author=work_author, work_title=work_title, uri=exercise_data.uri, urn=urn)
    # add the mapped exercise to the database
    db.session.add(new_exercise)
    ui_exercises: UpdateInfo = UpdateInfo.query.filter_by(resource_type=ResourceType.exercise_list.name).first()
    ui_exercises.last_modified_time = datetime.utcnow()
    db.session.commit()
    return new_exercise
