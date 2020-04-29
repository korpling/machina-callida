import json
import os
import re
import subprocess
from collections import OrderedDict
from sys import platform
from tempfile import mkstemp
from typing import List, Dict

import requests
from bs4 import BeautifulSoup, ResultSet, Tag
from conllu import TokenList
from flask_restful import Resource, reqparse

from mcserver.app.models import ExerciseType, ExerciseData, LinkMC, NodeMC
from mcserver.app.services import AnnotationService, NetworkService
from mcserver.config import Config


class KwicAPI(Resource):
    """The KWIC API resource. It gives users example contexts for a given phenomenon in a given corpus."""

    def __init__(self):
        """Initializes possible arguments for calls to the KWIC REST API."""
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("urn", type=str, required=True, default="", location="form", help="No URN provided")
        self.reqparse.add_argument("search_values", type=str, required=True, location="form",
                                   help="No search value(s) provided")
        self.reqparse.add_argument("ctx_left", type=int, required=False, location="form", default=5,
                                   help="No left context size provided")
        self.reqparse.add_argument("ctx_right", type=int, required=False, location="form", default=5,
                                   help="No left context size provided")
        super(KwicAPI, self).__init__()

    def post(self) -> object:
        """ The POST method for the KWIC REST API. It provides example contexts for a given phenomenon
        in a given corpus. """
        args = self.reqparse.parse_args()
        search_values_list: List[str] = json.loads(args["search_values"])
        aqls: List[str] = AnnotationService.map_search_values_to_aql(search_values_list, ExerciseType.kwic)
        ctx_left: int = args["ctx_left"]
        ctx_right: int = args["ctx_right"]
        url: str = f"{Config.INTERNET_PROTOCOL}{Config.HOST_IP_CSM}:{Config.CORPUS_STORAGE_MANAGER_PORT}{Config.SERVER_URI_CSM_SUBGRAPH}"
        data: str = json.dumps(dict(urn=args["urn"], aqls=aqls, ctx_left=str(ctx_left), ctx_right=str(ctx_right)))
        response: requests.Response = requests.post(url, data=data)
        response_content: List[dict] = json.loads(response.text)
        exercise_data_list: List[ExerciseData] = [ExerciseData(json_dict=x) for x in response_content]
        ret_val: str = ""
        for i in range(len(exercise_data_list)):
            ret_val += handle_exercise_data(exercise_data_list[i], ctx_left, ctx_right)
        return NetworkService.make_json_response(ret_val)


def handle_exercise_data(ed: ExerciseData, ctx_left: int, ctx_right: int) -> str:
    """ Constructs an SVG image (for POS and syntactic dependencies) from given annotations. """
    conllu_list: List[TokenList] = []
    dep_links: List[LinkMC] = [x for x in ed.graph.links if x.annis_component_name == Config.GRAPHANNIS_DEPENDENCY_LINK]
    current_sentence_id: str = "-1"
    salt_id_to_conll_id_dict: Dict[str, str] = {}
    for node in ed.graph.nodes:
        new_sentence_id: str = str(AnnotationService.get_sentence_id(node))
        if new_sentence_id != current_sentence_id:
            update_heads(conllu_list=conllu_list, salt_id_to_conll_id_dict=salt_id_to_conll_id_dict)
            conllu_list.append(TokenList(tokens=[], metadata=OrderedDict([("sent_id", new_sentence_id)])))
            current_sentence_id = new_sentence_id
            salt_id_to_conll_id_dict = {}
        relevant_link: LinkMC = next((x for x in dep_links if x.target == node.id), None)
        salt_id_to_conll_id_dict[node.id] = str(len(conllu_list[-1].tokens) + 1)
        conllu_list[-1].tokens.append(
            {"id": salt_id_to_conll_id_dict[node.id], "form": node.annis_tok, "lemma": node.udep_lemma,
             "upostag": node.udep_upostag, "xpostag": node.udep_xpostag, "feats": node.udep_feats,
             "head": "0" if relevant_link is None else relevant_link.source,
             Config.AQL_DEPREL: "root" if (
                     relevant_link is None or not hasattr(relevant_link,
                                                          "udep_deprel")) else relevant_link.udep_deprel,
             "deps": None, "misc": None})
    update_heads(conllu_list=conllu_list, salt_id_to_conll_id_dict=salt_id_to_conll_id_dict)
    conllu_string: str = "".join(x.tokens.serialize() for x in conllu_list)
    # generate temp file
    (handle, tmp_file_path) = mkstemp(suffix=".conllu")
    with open(tmp_file_path, "w+") as f:
        f.write(conllu_string)
    conllu2svg_path: str = Config.CONLLU2SVG_PATH_OSX if platform == Config.PLATFORM_MACOS else Config.CONLLU2SVG_PATH_LINUX
    html_bytes: bytes = subprocess.check_output("{0} {1}".format(conllu2svg_path, tmp_file_path), shell=True)
    os.remove(tmp_file_path)
    html_string: str = html_bytes.decode('utf-8')
    svg_list: List[str] = re.findall(r"<svg[\s\S]*?svg>", html_string)
    ret_val: str = "".join(svg_list) + "<br>"
    ret_val = re.sub(r' onclick=".*?"', "", ret_val)
    ret_val = re.sub(r' onmouseover=".*?"', "", ret_val)
    ret_val = re.sub(r' onmouseout=".*?"', "", ret_val)
    return highlight_targets(ret_val, ctx_left, ctx_right, ed)


def highlight_targets(html: str, ctx_left: int, ctx_right: int, ed: ExerciseData) -> str:
    """ Highlights the query terms in the SVG visualization. """
    max_len: int = ctx_left + ctx_right + 1
    soup: BeautifulSoup = BeautifulSoup(html, 'html.parser')
    text_groups: ResultSet = soup.find_all("g", {"font-style": "italic"})
    text_sets: List[ResultSet] = []
    for tg in text_groups:
        texts: ResultSet = tg.find_all("text")
        if len(texts):
            text_sets.append(texts)
    for i in range(len(text_sets)):
        target_text: Tag = Tag(name="")
        if len(text_sets[i]) == max_len:
            target_text = text_sets[i][ctx_left]
        else:
            target_node: NodeMC = next(x for x in ed.graph.nodes if x.id == ed.solutions[0].target.salt_id)
            for j in range(len(text_sets[i])):
                if text_sets[i][j].text == target_node.annis_tok:
                    target_text = text_sets[i][j]
                    break
        target_text["style"] = "fill: red"
    return str(soup)


def update_heads(conllu_list: List[TokenList], salt_id_to_conll_id_dict: Dict[str, str]) -> None:
    """ Updates the heads for given CONLLU data. """
    if len(conllu_list) > 0:
        for tok in conllu_list[-1].tokens:
            head: str = tok["head"]
            if head != "0":
                tok["head"] = salt_id_to_conll_id_dict[head]
                tok["deps"] = [(tok[Config.AQL_DEPREL], salt_id_to_conll_id_dict[head])]
