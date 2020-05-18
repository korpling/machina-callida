import json
from typing import List

from flask_restful import Resource, abort
from flask_restful.reqparse import RequestParser

from mcserver.app import db
from mcserver.app.models import Language, ExerciseType, Solution
from mcserver.app.services import TextService, NetworkService
from mcserver.models_auto import Exercise


class H5pAPI(Resource):
    """The H5P API resource. It gives users access to interactive exercise layouts."""

    def __init__(self):
        """Initialize possible arguments for calls to the H5P REST API."""
        self.reqparse: RequestParser = NetworkService.base_request_parser.copy()
        self.reqparse.add_argument("eid", type=str, required=True, default="", help="No exercise ID provided")
        self.reqparse.add_argument("lang", type=str, required=True, default="en", help="No language code provided")
        self.reqparse.add_argument("solution_indices", type=str, required=False, help="No solution IDs provided")
        self.feedback_template: str = "{0}: @score {1} @total."
        self.json_template_drag_text: dict = {
            "taskDescription": "<p>{0}</p>\n",
            "checkAnswer": "Prüfen",
            "tryAgain": "Nochmal",
            "showSolution": "Lösung",
            "behaviour": {
                "enableRetry": True,
                "enableSolutionsButton": True,
                "instantFeedback": False,
                "enableCheckButton": True
            },
            "textField": "Blueberries are *blue:Check the name of the berry!*.\nStrawberries are *red*.",
            "overallFeedback": [{"from": 0, "to": 100, "feedback": "Punkte: @score von @total."}],
            "dropZoneIndex": "Drop Zone @index.",
            "empty": "Drop Zone @index is empty.",
            "contains": "Drop Zone @index contains draggable @draggable.",
            "draggableIndex": "Draggable @text. @index of @count draggables.",
            "tipLabel": "Show tip",
            "correctText": "Correct!",
            "incorrectText": "Incorrect!",
            "resetDropTitle": "Reset drop",
            "resetDropDescription": "Are you sure you want to reset this drop zone?",
            "grabbed": "Draggable is grabbed.",
            "cancelledDragging": "Cancelled dragging.",
            "correctAnswer": "Correct answer:",
            "feedbackHeader": "Feedback",
            "scoreBarLabel": "You got :num out of :total points"
        }
        self.json_template_mark_words: dict = {
            "checkAnswerButton": "Check",
            "tryAgainButton": "Retry",
            "showSolutionButton": "Show solution",
            "behaviour": {
                "enableRetry": True,
                "enableSolutionsButton": True
            },
            "taskDescription": "<p>Click the various types of berries&nbsp;mentioned&nbsp;in the text below!<\/p>\n",
            "textField": "*Bilberries*, also known as *blueberries* are edible, nearly black berries found in nutrient-poor soils.<br><br>*Cloudberries* are edible orange berries similar to *raspberries* or *blackberries* found in alpine and arctic tundra. <br><br>*Redcurrants* are red translucent berries with a diameter of 8\u201310 mm, and are closely related to *blackcurrants*.",
            "overallFeedback": [{"from": 0, "to": 100, "feedback": "You got @score of @total points."}]
        }
        super(H5pAPI, self).__init__()

    def get(self):
        """ The GET method for the H5P REST API. It provides json templates for client-side H5P exercise layouts. """
        args = self.reqparse.parse_args()
        eid: str = args["eid"]
        solution_indices: List[int] = json.loads(args["solution_indices"] if args["solution_indices"] else "null")
        lang: Language
        try:
            lang = Language(args["lang"])
        except ValueError:
            lang = Language.English
        exercise: Exercise = db.session.query(Exercise).filter_by(eid=eid).first()
        db.session.commit()
        if exercise is None:
            abort(404)
        text_field_content: str = ""
        if exercise.exercise_type in [ExerciseType.cloze.value, ExerciseType.markWords.value]:
            text_field_content = TextService.get_h5p_text_with_solutions(exercise, solution_indices)
        elif exercise.exercise_type == ExerciseType.matching.value:
            solutions: List[Solution] = TextService.get_solutions_by_index(exercise, solution_indices)
            for solution in solutions:
                text_field_content += "{0} *{1}*\n".format(solution.target.content, solution.value.content)
        else:
            abort(422)
        response_dict: dict = self.json_template_mark_words
        response_dict = get_response(response_dict, lang, self.json_template_drag_text, exercise, text_field_content,
                                     self.feedback_template)
        return NetworkService.make_json_response(response_dict)


def get_response(response_dict: dict, lang: Language, json_template_drag_text: dict, exercise: Exercise,
                 text_field_content: str, feedback_template: str):
    # default values for buttons and response
    button_dict: dict = {"check": ["checkAnswerButton", "Prüfen" if lang == Language.German else "Check"],
                         "again": ["tryAgainButton", "Nochmal" if lang == Language.German else "Retry"],
                         "solution": ["showSolutionButton", "Lösung" if lang == Language.German else "Solution"]}
    if exercise.exercise_type != ExerciseType.markWords.value:
        button_dict["check"][0] = "checkAnswer"
        button_dict["again"][0] = "tryAgain"
        button_dict["solution"][0] = "showSolution"
        response_dict = json_template_drag_text
    for button in button_dict:
        response_dict[button_dict[button][0]] = button_dict[button][1]
    response_dict["taskDescription"] = "<p>{0}: {1}</p>\n".format(exercise.exercise_type_translation,
                                                                  exercise.instructions)
    response_dict["textField"] = text_field_content
    feedback: str = feedback_template.format("Punkte", "von")
    if lang != Language.German:
        feedback = feedback_template.format("Score", "of")
    response_dict["overallFeedback"][0]["feedback"] = feedback
    return response_dict
