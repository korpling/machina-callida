import json
from typing import Dict, List
import flask
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from mcserver.app.models import ExerciseData, GraphData, Solution, AnnisResponse, make_solution_element_from_salt_id
from mcserver.app.services import CorpusService, AnnotationService, NetworkService


class SubgraphAPI(Resource):
    def __init__(self):
        self.reqparse: RequestParser = NetworkService.base_request_parser.copy()
        self.reqparse.add_argument("aqls", required=False, location="data", help="No AQLs provided", action="append")
        self.reqparse.add_argument("ctx_left", type=str, required=False, default="", location="data",
                                   help="No left context provided")
        self.reqparse.add_argument("ctx_right", type=str, required=False, default="", location="data",
                                   help="No right context provided")
        self.reqparse.add_argument("node_ids", type=str, required=False, location="data", help="No node IDs provided")
        self.reqparse.add_argument("urn", type=str, required=False, default="", location="data", help="No URN provided")
        super(SubgraphAPI, self).__init__()

    def get(self):
        """ Returns subgraph data for a given CTS URN and node IDs. """
        args: Dict = flask.request.args
        aql: str = str(args['aqls'])
        urn: str = args["urn"]
        ctx_left: int = int(args["ctx_left"])
        ctx_right: int = int(args["ctx_right"])
        ar: AnnisResponse = CorpusService.get_subgraph(urn, aql, ctx_left, ctx_right, is_csm=True)
        return NetworkService.make_json_response(ar.to_dict())

    def post(self):
        """ Returns subgraph data for a given CTS URN and AQL. """
        # get request arguments
        args: Dict = json.loads(flask.request.data.decode("utf-8"))
        cts_urn: str = args["urn"]
        aqls: List[str] = args["aqls"]
        ctx_left: int = int(args["ctx_left"])
        ctx_right: int = int(args["ctx_right"])
        disk_urn: str = AnnotationService.get_disk_urn(cts_urn)
        exercise_data_list: List[ExerciseData] = []
        for aql in aqls:
            node_ids: List[str] = CorpusService.find_matches(cts_urn, aql, is_csm=True)
            for node_id in node_ids:
                gd: GraphData = AnnotationService.get_single_subgraph(
                    disk_urn, [node_id], ctx_left, ctx_right, is_csm=True)
                exercise_data_list.append(ExerciseData(
                    graph=gd, uri="", solutions=[Solution(target=make_solution_element_from_salt_id(node_id))]))
        ret_val: List[dict] = [x.serialize() for x in exercise_data_list]
        return NetworkService.make_json_response(ret_val)
