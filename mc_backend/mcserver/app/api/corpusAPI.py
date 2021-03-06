"""The corpus API. Add it to your REST API to provide users with metadata about specific texts."""
from typing import Union

import connexion
from connexion.lifecycle import ConnexionResponse
from flask import Response

from mcserver import Config
from mcserver.app import db
from mcserver.app.services import NetworkService, DatabaseService
from mcserver.models_auto import Corpus


def delete(cid: int) -> Union[Response, ConnexionResponse]:
    """The DELETE method for the corpus REST API. It deletes metadata for a specific text."""
    corpus: Corpus = DatabaseService.query(Corpus, filter_by=dict(cid=cid), first=True)
    if not corpus:
        return connexion.problem(404, Config.ERROR_TITLE_NOT_FOUND, Config.ERROR_MESSAGE_CORPUS_NOT_FOUND)
    db.session.delete(corpus)
    DatabaseService.commit()
    return NetworkService.make_json_response(True)


def get(cid: int) -> Union[Response, ConnexionResponse]:
    """The GET method for the corpus REST API. It provides metadata for a specific text."""
    corpus: Corpus = DatabaseService.query(Corpus, filter_by=dict(cid=cid), first=True)
    if not corpus:
        return connexion.problem(404, Config.ERROR_TITLE_NOT_FOUND, Config.ERROR_MESSAGE_CORPUS_NOT_FOUND)
    return NetworkService.make_json_response(corpus.to_dict())


def patch(cid: int, **kwargs) -> Union[Response, ConnexionResponse]:
    """The PUT method for the corpus REST API. It provides updates metadata for a specific text."""
    corpus: Corpus = DatabaseService.query(Corpus, filter_by=dict(cid=cid), first=True)
    if not corpus:
        return connexion.problem(404, Config.ERROR_TITLE_NOT_FOUND, Config.ERROR_MESSAGE_CORPUS_NOT_FOUND)
    for k, v in kwargs.items():
        if v is not None:
            setattr(corpus, k, v)
    DatabaseService.commit()
    return NetworkService.make_json_response(corpus.to_dict())
