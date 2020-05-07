"""The corpus API. Add it to your REST API to provide users with metadata about specific texts."""
from flask_restful import Resource, abort, marshal
from flask_restful.reqparse import RequestParser

from mcserver.app import db
from mcserver.app.models import Corpus, corpus_fields
from mcserver.app.services import NetworkService


class CorpusAPI(Resource):
    """The corpus API resource. It enables some of the CRUD operations for metadata about specific texts."""

    def __init__(self):
        """Initialize possible arguments for calls to the corpus REST API."""
        self.reqparse: RequestParser = NetworkService.base_request_parser.copy()
        self.reqparse.add_argument("title", type=str, required=False, help="No title provided")
        self.reqparse.add_argument("author", type=str, required=False, help="No author provided")
        self.reqparse.add_argument("source_urn", type=str, required=False, help="No source URN provided")
        super(CorpusAPI, self).__init__()

    def get(self, cid):
        """The GET method for the corpus REST API. It provides metadata for a specific text."""
        corpus: Corpus = Corpus.query.filter_by(cid=cid).first()
        if corpus is None:
            abort(404)
        return {"corpus": marshal(corpus, corpus_fields)}

    def put(self, cid):
        """The PUT method for the corpus REST API. It provides updates metadata for a specific text."""
        corpus: Corpus = Corpus.query.filter_by(cid=cid).first()
        if corpus is None:
            abort(404)
        args = self.reqparse.parse_args()
        for k, v in args.items():
            if v is not None:
                setattr(corpus, k, v)
        db.session.commit()
        return {"corpus": marshal(corpus, corpus_fields)}

    def delete(self, cid):
        """The DELETE method for the corpus REST API. It deletes metadata for a specific text."""
        corpus: Corpus = Corpus.query.filter_by(cid=cid).first()
        if corpus is None:
            abort(404)
        db.session.delete(corpus)
        db.session.commit()
        return {"result": True}
