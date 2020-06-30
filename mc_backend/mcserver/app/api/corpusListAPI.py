"""The corpus list API. Add it to your REST API to provide users with a list of metadata for available texts."""
from connexion.lifecycle import ConnexionResponse
from flask import Response
from typing import List, Union
from mcserver.app import db
from mcserver.app.models import ResourceType
from mcserver.app.services import NetworkService, DatabaseService
from mcserver.models_auto import Corpus, UpdateInfo


def get(last_update_time: int) -> Union[Response, ConnexionResponse]:
    """The GET method for the corpus list REST API. It provides metadata for all available texts."""
    ui_cts: UpdateInfo
    ui_cts = db.session.query(UpdateInfo).filter_by(resource_type=ResourceType.cts_data.name).first()
    DatabaseService.commit()
    if ui_cts.last_modified_time >= last_update_time / 1000:
        corpora: List[Corpus] = db.session.query(Corpus).all()
        DatabaseService.commit()
        return NetworkService.make_json_response([x.to_dict() for x in corpora])
    return NetworkService.make_json_response(None)
