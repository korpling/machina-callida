"""The corpus list API. Add it to your REST API to provide users with a list of metadata for available texts."""
from connexion.lifecycle import ConnexionResponse
from flask import Response
from typing import List, Union
from mcserver.app.models import ResourceType
from mcserver.app.services import NetworkService, DatabaseService
from mcserver.models_auto import Corpus, UpdateInfo


def get(last_update_time: int) -> Union[Response, ConnexionResponse]:
    """The GET method for the corpus list REST API. It provides metadata for all available texts."""
    ui_cts: UpdateInfo = DatabaseService.query(
        UpdateInfo, filter_by=dict(resource_type=ResourceType.cts_data.name), first=True)
    if ui_cts and ui_cts.last_modified_time >= last_update_time / 1000:
        corpora: List[Corpus] = DatabaseService.query(Corpus)
        return NetworkService.make_json_response([x.to_dict() for x in corpora])
    return NetworkService.make_json_response(None)
