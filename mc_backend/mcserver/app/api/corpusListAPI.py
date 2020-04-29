"""The corpus list API. Add it to your REST API to provide users with a list of metadata for available texts."""
from datetime import datetime

from flask import jsonify
from flask_restful import Resource, reqparse, marshal
from sqlalchemy.exc import OperationalError, InvalidRequestError

from mcserver.app import db
from mcserver.app.models import UpdateInfo, ResourceType, Corpus, corpus_fields
from mcserver.app.services import CorpusService


class CorpusListAPI(Resource):
    """The corpus list API resource. It enables some of the CRUD operations for a list of metadata about all texts."""

    def __init__(self):
        """Initialize possible arguments for calls to the corpus list REST API."""
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("last_update_time", type=int, required=True,
                                   help="No milliseconds time for last update provided")
        super(CorpusListAPI, self).__init__()

    def get(self):
        """The GET method for the corpus list REST API. It provides metadata for all available texts."""
        args = self.reqparse.parse_args()
        last_update: int = args["last_update_time"]
        last_update_time: datetime = datetime.fromtimestamp(last_update / 1000.0)
        ui_cts: UpdateInfo
        try:
            ui_cts = UpdateInfo.query.filter_by(resource_type=ResourceType.cts_data.name).first()
        except (InvalidRequestError, OperationalError):
            db.session.rollback()
            return None
        if ui_cts.last_modified_time >= last_update_time:
            CorpusService.existing_corpora = Corpus.query.all()
            return jsonify({"corpora": [marshal(corpus, corpus_fields) for corpus in CorpusService.existing_corpora]})
        return None
