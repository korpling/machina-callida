"""The file API. Add it to your REST API to provide users access to specific files."""
import json
import os
import uuid
from datetime import datetime
from typing import List, Union
import connexion
from connexion.lifecycle import ConnexionResponse
from flask import send_from_directory, Response
from werkzeug.wrappers import ETagResponseMixin
from mcserver.app import db
from mcserver.app.models import FileType, ResourceType, DownloadableFile, MimeType, XapiStatement, LearningResultMC
from mcserver.app.services import FileService, NetworkService
from mcserver.config import Config
from mcserver.models_auto import Exercise, UpdateInfo, LearningResult


def clean_tmp_folder():
    """ Cleans the files directory regularly. """
    ui_file: UpdateInfo = db.session.query(UpdateInfo).filter_by(resource_type=ResourceType.file_api_clean.name).first()
    ui_datetime: datetime = datetime.fromtimestamp(ui_file.last_modified_time)
    if (datetime.utcnow() - ui_datetime).total_seconds() > Config.INTERVAL_FILE_DELETE:
        for file in [x for x in os.listdir(Config.TMP_DIRECTORY) if x not in ".gitignore"]:
            file_to_delete_type: str = os.path.splitext(file)[1].replace(".", "")
            file_to_delete: DownloadableFile = next((x for x in FileService.downloadable_files if
                                                     x.file_name == file and x.file_type == file_to_delete_type),
                                                    None)
            if file_to_delete is not None:
                FileService.downloadable_files.remove(file_to_delete)
            os.remove(os.path.join(Config.TMP_DIRECTORY, file))
            ui_file.last_modified_time = datetime.utcnow().timestamp()
            db.session.commit()


def get(id: str, type: FileType, solution_indices: List[int]) -> Union[ETagResponseMixin, ConnexionResponse]:
    """The GET method for the file REST API. It provides the URL to download a specific file."""
    clean_tmp_folder()
    exercise: Exercise = db.session.query(Exercise).filter_by(eid=id).first()
    db.session.commit()
    file_name: str = id + "." + str(type)
    mime_type: str = MimeType[type].value
    if exercise is None:
        # try and see if a file is already cached on disk
        if not os.path.exists(os.path.join(Config.TMP_DIRECTORY, file_name)):
            return connexion.problem(404, Config.ERROR_TITLE_NOT_FOUND, Config.ERROR_MESSAGE_EXERCISE_NOT_FOUND)
        return send_from_directory(Config.TMP_DIRECTORY, file_name, mimetype=mime_type, as_attachment=True)
    exercise.last_access_time = datetime.utcnow().timestamp()
    db.session.commit()
    if solution_indices:
        file_name = id + "-" + str(uuid.uuid4()) + "." + str(type)
    existing_file: DownloadableFile = next(
        (x for x in FileService.downloadable_files if x.id + "." + str(x.file_type) == file_name), None)
    if existing_file is None:
        existing_file = FileService.make_tmp_file_from_exercise(type, exercise, solution_indices)
    return send_from_directory(Config.TMP_DIRECTORY, existing_file.file_name, mimetype=mime_type,
                               as_attachment=True)


def post(file_data: dict) -> Response:
    """ The POST method for the File REST API.

    It writes learning results or HTML content to the disk for later access. """
    lr_string: str = file_data.get("learning_result", None)
    if lr_string:
        lr_dict: dict = json.loads(lr_string)
        for exercise_id in lr_dict:
            xapi_statement: XapiStatement = XapiStatement(lr_dict[exercise_id])
            save_learning_result(xapi_statement)
        return NetworkService.make_json_response(str(True))
    else:
        file_type: FileType = file_data["file_type"]
        existing_file: DownloadableFile = FileService.make_tmp_file_from_html(file_data["urn"], file_type,
                                                                              file_data["html_content"])
        return NetworkService.make_json_response(existing_file.file_name)


def save_learning_result(xapi_statement: XapiStatement) -> LearningResult:
    """Creates a new Learning Result from a XAPI Statement and saves it to the database."""
    learning_result: LearningResult = LearningResultMC.from_dict(
        actor_account_name=xapi_statement.actor.account.name,
        actor_object_type=xapi_statement.actor.object_type.value,
        category_id=xapi_statement.context.context_activities.category[0].id,
        category_object_type=xapi_statement.context.context_activities.category[0].object_type.value,
        choices=json.dumps([x.serialize() for x in xapi_statement.object.definition.choices]),
        completion=xapi_statement.result.completion,
        correct_responses_pattern=json.dumps(xapi_statement.object.definition.correct_responses_pattern),
        created_time=datetime.utcnow().timestamp(),
        duration=xapi_statement.result.duration,
        extensions=json.dumps(xapi_statement.object.definition.extensions),
        interaction_type=xapi_statement.object.definition.interaction_type,
        object_definition_description=xapi_statement.object.definition.description.en_us,
        object_definition_type=xapi_statement.object.definition.type,
        object_object_type=xapi_statement.object.object_type.value,
        response=xapi_statement.result.response,
        score_max=xapi_statement.result.score.max,
        score_min=xapi_statement.result.score.min,
        score_raw=xapi_statement.result.score.raw,
        score_scaled=xapi_statement.result.score.scaled,
        success=xapi_statement.result.success,
        verb_id=xapi_statement.verb.id,
        verb_display=xapi_statement.verb.display.en_us
    )
    db.session.add(learning_result)
    db.session.commit()
    return learning_result
