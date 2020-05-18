"""The file API. Add it to your REST API to provide users access to specific files."""
import json
import os
import uuid
from datetime import datetime
from typing import List, Union

import flask
from flask import send_from_directory
from flask_restful import Resource, abort
from flask_restful.reqparse import RequestParser
from werkzeug.wrappers import ETagResponseMixin

from mcserver.app import db
from mcserver.app.models import FileType, ResourceType, DownloadableFile, MimeType, XapiStatement, LearningResultMC
from mcserver.app.services import FileService, NetworkService
from mcserver.config import Config
from mcserver.models_auto import Exercise, UpdateInfo, LearningResult


class FileAPI(Resource):
    """The file API resource. It allows users to download files that are stored as strings in the database."""

    def __init__(self):
        """Initialize possible arguments for calls to the file REST API."""
        self.reqparse: RequestParser = NetworkService.base_request_parser.copy()
        self.reqparse.add_argument("id", type=str, required=False, location="args",
                                   help="No exercise ID or URN provided")
        self.reqparse.add_argument("type", type=str, required=False, location="args", help="No file type provided")
        self.reqparse.add_argument("solution_indices", type=str, required=False, location="args",
                                   help="No solution IDs provided")
        self.reqparse.add_argument("learning_result", type=str, required=False, location="form",
                                   help="No learning result provided")
        self.reqparse.add_argument("html_content", type=str, required=False, location="form",
                                   help="No HTML content provided")
        self.reqparse.add_argument("file_type", type=str, required=False, location="form",
                                   help="No file type provided")
        self.reqparse.add_argument("urn", type=str, required=False, location="form", help="No URN provided")
        super(FileAPI, self).__init__()

    def get(self) -> ETagResponseMixin:
        """The GET method for the file REST API. It provides the URL to download a specific file."""
        clean_tmp_folder()
        args = self.reqparse.parse_args()
        eid: str = args["id"]
        exercise: Exercise = db.session.query(Exercise).filter_by(eid=eid).first()
        db.session.commit()
        file_type: FileType = FileType[args["type"]]
        file_name: str = eid + "." + file_type.value
        mime_type: str = MimeType[file_type.value].value
        if exercise is None:
            # try and see if a file is already cached on disk
            if not os.path.exists(os.path.join(Config.TMP_DIRECTORY, file_name)):
                abort(404)
            return send_from_directory(Config.TMP_DIRECTORY, file_name, mimetype=mime_type, as_attachment=True)
        exercise.last_access_time = datetime.utcnow().timestamp()
        db.session.commit()
        solution_indices: List[int] = json.loads(args["solution_indices"] if args["solution_indices"] else "null")
        if solution_indices is not None:
            file_name = eid + "-" + str(uuid.uuid4()) + "." + file_type.value
        existing_file: DownloadableFile = next(
            (x for x in FileService.downloadable_files if x.id + "." + x.file_type.value == file_name), None)
        if existing_file is None:
            existing_file = FileService.make_tmp_file_from_exercise(file_type, exercise, solution_indices)
        return send_from_directory(Config.TMP_DIRECTORY, existing_file.file_name, mimetype=mime_type,
                                   as_attachment=True)

    def post(self) -> Union[None, ETagResponseMixin]:
        """ The POST method for the File REST API.

        It writes learning results or HTML content to the disk for later access. """
        form_data: dict = flask.request.form
        lr_string: str = form_data.get("learning_result", None)
        if lr_string:
            lr_dict: dict = json.loads(lr_string)
            for exercise_id in lr_dict:
                xapi_statement: XapiStatement = XapiStatement(lr_dict[exercise_id])
                save_learning_result(xapi_statement)
        else:
            file_type: FileType = FileType[form_data["file_type"]]
            existing_file: DownloadableFile = FileService.make_tmp_file_from_html(form_data["urn"], file_type,
                                                                                  form_data["html_content"])
            return NetworkService.make_json_response(existing_file.file_name)


def clean_tmp_folder():
    """ Cleans the files directory regularly. """
    ui_file: UpdateInfo = db.session.query(UpdateInfo).filter_by(resource_type=ResourceType.file_api_clean.name).first()
    ui_datetime: datetime = datetime.fromtimestamp(ui_file.last_modified_time)
    if (datetime.utcnow() - ui_datetime).total_seconds() > Config.INTERVAL_FILE_DELETE:
        for file in [x for x in os.listdir(Config.TMP_DIRECTORY) if x not in ".gitignore"]:
            file_to_delete_type: str = os.path.splitext(file)[1].replace(".", "")
            file_to_delete: DownloadableFile = next((x for x in FileService.downloadable_files if
                                                     x.file_name == file and x.file_type.value == file_to_delete_type),
                                                    None)
            if file_to_delete is not None:
                FileService.downloadable_files.remove(file_to_delete)
            os.remove(os.path.join(Config.TMP_DIRECTORY, file))
            ui_file.last_modified_time = datetime.utcnow().timestamp()
            db.session.commit()


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
