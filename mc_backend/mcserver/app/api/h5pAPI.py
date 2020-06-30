from typing import List, Union
import connexion
from connexion.lifecycle import ConnexionResponse
from flask import Response
from mcserver import Config
from mcserver.app import db
from mcserver.app.models import Language, ExerciseType, Solution
from mcserver.app.services import TextService, NetworkService, DatabaseService
from mcserver.models_auto import Exercise


def get(eid: str, lang: str, solution_indices: List[int]) -> Union[Response, ConnexionResponse]:
    """ The GET method for the H5P REST API. It provides JSON templates for client-side H5P exercise layouts. """
    language: Language
    try:
        language = Language(lang)
    except ValueError:
        language = Language.English
    exercise: Exercise = db.session.query(Exercise).filter_by(eid=eid).first()
    DatabaseService.commit()
    if exercise is None:
        return connexion.problem(404, Config.ERROR_TITLE_NOT_FOUND, Config.ERROR_MESSAGE_EXERCISE_NOT_FOUND)
    text_field_content: str = ""
    if exercise.exercise_type in [ExerciseType.cloze.value, ExerciseType.markWords.value]:
        text_field_content = TextService.get_h5p_text_with_solutions(exercise, solution_indices)
    elif exercise.exercise_type == ExerciseType.matching.value:
        solutions: List[Solution] = TextService.get_solutions_by_index(exercise, solution_indices)
        for solution in solutions:
            text_field_content += "{0} *{1}*\n".format(solution.target.content, solution.value.content)
    else:
        return connexion.problem(
            422, Config.ERROR_TITLE_UNPROCESSABLE_ENTITY, Config.ERROR_MESSAGE_UNPROCESSABLE_ENTITY)
    response_dict: dict = TextService.json_template_mark_words
    response_dict = get_response(response_dict, language, TextService.json_template_drag_text, exercise,
                                 text_field_content, TextService.feedback_template)
    return NetworkService.make_json_response(response_dict)


def get_response(response_dict: dict, lang: Language, json_template_drag_text: dict, exercise: Exercise,
                 text_field_content: str, feedback_template: str) -> dict:
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
