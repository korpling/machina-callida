import json
import os
import shutil
import zipfile
from typing import List, Union, Set
import connexion
from connexion.lifecycle import ConnexionResponse
from flask import Response, send_from_directory
from mcserver import Config
from mcserver.app import db
from mcserver.app.models import Language, ExerciseType, Solution, MimeType, FileType
from mcserver.app.services import TextService, NetworkService, DatabaseService
from mcserver.models_auto import Exercise
from openapi.openapi_server.models import H5PForm


def determine_language(lang: str) -> Language:
    """Convert the given language ISO code to our internal enum-style representation of languages."""
    language: Language
    try:
        language = Language(lang)
    except ValueError:
        language = Language.English
    return language


def get(eid: str, lang: str, solution_indices: List[int]) -> Union[Response, ConnexionResponse]:
    """ The GET method for the H5P REST API. It provides JSON templates for client-side H5P exercise layouts. """
    language: Language = determine_language(lang)
    exercise: Exercise = db.session.query(Exercise).filter_by(eid=eid).first()
    DatabaseService.commit()
    if exercise is None:
        return connexion.problem(404, Config.ERROR_TITLE_NOT_FOUND, Config.ERROR_MESSAGE_EXERCISE_NOT_FOUND)
    text_field_content: str = get_text_field_content(exercise, solution_indices)
    if not text_field_content:
        return connexion.problem(
            422, Config.ERROR_TITLE_UNPROCESSABLE_ENTITY, Config.ERROR_MESSAGE_UNPROCESSABLE_ENTITY)
    response_dict: dict = TextService.json_template_mark_words
    response_dict = get_response(response_dict, language, TextService.json_template_drag_text, exercise,
                                 text_field_content, TextService.feedback_template)
    return NetworkService.make_json_response(response_dict)


def get_response(response_dict: dict, lang: Language, json_template_drag_text: dict, exercise: Exercise,
                 text_field_content: str, feedback_template: str) -> dict:
    """Perform localization for an existing H5P exercise template and insert the relevant exercise materials."""
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


def get_text_field_content(exercise: Exercise, solution_indices: List[int]) -> str:
    """Build the text field content for a H5P exercise, i.e. the task, exercise material and solutions."""
    text_field_content: str = ""
    if exercise.exercise_type in [ExerciseType.cloze.value, ExerciseType.markWords.value]:
        text_field_content = TextService.get_h5p_text_with_solutions(exercise, solution_indices)
    elif exercise.exercise_type == ExerciseType.matching.value:
        solutions: List[Solution] = TextService.get_solutions_by_index(exercise, solution_indices)
        for solution in solutions:
            text_field_content += "{0} *{1}*\n".format(solution.target.content, solution.value.content)
    return text_field_content


def make_h5p_archive(file_name_no_ext: str, response_dict: dict, target_dir: str, file_name: str):
    """Creates a H5P archive (in ZIP format) for a given exercise."""
    source_dir: str = os.path.join(Config.H5P_DIRECTORY, file_name_no_ext)
    content_dir: str = os.path.join(Config.TMP_DIRECTORY, "content")
    os.makedirs(content_dir, exist_ok=True)
    content_file_path: str = os.path.join(content_dir, "content.json")
    json.dump(response_dict, open(content_file_path, "w+"))
    # exclude empty directories from the archive because the Moodle H5P importer cannot handle them
    white_list: Set[str] = {'.svg', '.otf', '.json', '.css', '.diff', '.woff', '.eot', '.png', '.gif',
                            '.woff2', '.js', '.ttf'}
    with zipfile.ZipFile(os.path.join(target_dir, file_name), "w") as zipObj:
        # Iterate over all the files in directory
        for folder_name, subfolders, file_names in os.walk(source_dir):
            if folder_name.endswith("content"):
                continue
            for new_file_name in file_names:
                # create complete filepath of file in directory
                new_file_path: str = os.path.join(folder_name, new_file_name)
                if os.path.splitext(new_file_path)[1] in white_list:
                    # Add file to zip
                    zipObj.write(filename=new_file_path, arcname=new_file_path.replace(source_dir, ""))
        zipObj.write(filename=content_file_path, arcname=content_file_path.replace(Config.TMP_DIRECTORY, ""))
    shutil.rmtree(content_dir)


def post(h5p_data: dict):
    """ The POST method for the H5P REST API. It offers client-side H5P exercises for download as ZIP archives. """
    h5p_form: H5PForm = H5PForm.from_dict(h5p_data)
    language: Language = determine_language(h5p_form.lang)
    exercise: Exercise = db.session.query(Exercise).filter_by(eid=h5p_form.eid).first()
    DatabaseService.commit()
    if exercise is None:
        return connexion.problem(404, Config.ERROR_TITLE_NOT_FOUND, Config.ERROR_MESSAGE_EXERCISE_NOT_FOUND)
    text_field_content: str = get_text_field_content(exercise, h5p_form.solution_indices)
    if not text_field_content:
        return connexion.problem(
            422, Config.ERROR_TITLE_UNPROCESSABLE_ENTITY, Config.ERROR_MESSAGE_UNPROCESSABLE_ENTITY)
    response_dict: dict = TextService.json_template_mark_words
    response_dict = get_response(response_dict, language, TextService.json_template_drag_text, exercise,
                                 text_field_content, TextService.feedback_template)
    file_name_no_ext: str = str(h5p_form.exercise_type_path)
    file_name: str = f"{file_name_no_ext}.{FileType.ZIP}"
    target_dir: str = Config.TMP_DIRECTORY
    make_h5p_archive(file_name_no_ext, response_dict, target_dir, file_name)
    return send_from_directory(target_dir, file_name, mimetype=MimeType.zip.value, as_attachment=True)
