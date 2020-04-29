"""The vector network API. Add it to your REST API to provide users with vector networks for a given AI model."""
import os
import re
from typing import List, Dict, Set, Tuple, Pattern
from flask_restful import Resource, reqparse
from gensim import matutils
from gensim.models import Word2Vec
from matplotlib import pyplot
from networkx import Graph, nx
from numpy.core.multiarray import ndarray, dot

from mcserver import Config
from mcserver.app.services import NetworkService


class VectorNetworkAPI(Resource):
    """The vector network API resource. It helps to manage network data for the vectors in an AI model."""

    def __init__(self):
        """Initialize possible arguments for calls to the corpus list REST API."""
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("search_regex", type=str, required=True,
                                   help="No regular expression provided for the search")
        self.reqparse.add_argument("min_count", type=int, required=False, default=1,
                                   help="No minimum count for word occurrences provided")
        self.reqparse.add_argument("highlight_regex", type=str, required=False, default="",
                                   help="No regular expression provided for highlighting")
        self.reqparse.add_argument("nearest_neighbor_count", type=int, required=False, default=0,
                                   help="No regular expression provided for highlighting")
        super(VectorNetworkAPI, self).__init__()

    def get(self):
        """The GET method for the vector network REST API. It provides network data for the vectors in an AI model."""
        args: dict = self.reqparse.parse_args()
        search_regex: str = args["search_regex"]
        min_count: int = args["min_count"]
        highlight_regex: str = args["highlight_regex"]
        nearest_neighbor_count: int = args["nearest_neighbor_count"]
        ret_val: str = get_concept_network(search_regex, min_count, highlight_regex, nearest_neighbor_count)
        return NetworkService.make_json_response(ret_val)

    def post(self):
        """
        The POST method for the vector network REST API. It provides sentences whose content is similar to a given word.
        """
        args: dict = self.reqparse.parse_args()
        search_regex_string: str = args["search_regex"]
        nearest_neighbor_count: int = args["nearest_neighbor_count"]
        nearest_neighbor_count = nearest_neighbor_count if nearest_neighbor_count else 10
        w2v: Word2Vec = Word2Vec.load(Config.PANEGYRICI_LATINI_MODEL_PATH)
        search_regex: Pattern[str] = re.compile(search_regex_string)
        keys: List[str] = [x for x in w2v.wv.vocab if search_regex.match(x)]
        relevant_vectors: List[ndarray] = [w2v.wv.get_vector(x) for x in keys]
        target_vector: ndarray = sum(relevant_vectors) / len(relevant_vectors)
        sentences: List[str] = open(Config.PANEGYRICI_LATINI_TEXT_PATH).readlines()
        sentence_vectors: Dict[int, ndarray] = {}
        for i in range(len(sentences)):
            toks: List[str] = sentences[i][:-1].split()
            if toks:
                vecs: List[ndarray] = []
                for tok in toks:
                    vector: ndarray = w2v.wv.get_vector(tok)
                    vecs.append(vector)
                sentence_vectors[i] = sum(vecs) / len(vecs)
        sims: List[Tuple[int, ndarray]] = []
        for key in sentence_vectors.keys():
            sims.append((key, dot(matutils.unitvec(target_vector), matutils.unitvec(sentence_vectors[key]))))
        sims.sort(key=lambda x: x[1], reverse=True)
        sims = sims[:nearest_neighbor_count]
        return [sentences[x[0]].split() for x in sims]


def add_edges(keys: List[str], w2v: Word2Vec, nearest_neighbor_count: int, min_count: int, graph: Graph) -> None:
    """Adds edges to an existing graph based on a list of keys and constraints to their similarity and frequency."""
    edge_dict: Dict[str, Set[str]] = {}
    for key in keys:
        sims: List[str] = [x[0] for x in w2v.wv.most_similar(key, topn=nearest_neighbor_count)]
        for i in range(len(sims)):
            if w2v.wv.vocab[sims[i]].count >= min_count:
                graph.add_edge(key, sims[i])
            sub_sims: List[str] = [x[0] for x in w2v.wv.most_similar(sims[i], topn=nearest_neighbor_count)]
            sub_sims = [x for x in sub_sims if w2v.wv.vocab[x].count >= min_count]
            for sub_sim in sub_sims:
                edge_dict[sims[i]] = edge_dict.get(sims[i], set()).union({sub_sim})
                edge_dict[sub_sim] = edge_dict.get(sub_sim, set()).union({sims[i]})
    for edge_source in edge_dict:
        if graph.has_node(edge_source):
            for edge_target in edge_dict[edge_source]:
                if graph.has_node(edge_target):
                    graph.add_edge(edge_source, edge_target)


def get_concept_network(search_regex_string: str, min_count: int = 1, highlight_regex_string: str = "",
                        nearest_neighbor_count: int = 0) -> str:
    """Extracts a network of words from vector data in an AI model."""
    graph: Graph = Graph()
    w2v: Word2Vec = Word2Vec.load(Config.PANEGYRICI_LATINI_MODEL_PATH)
    search_regex: Pattern[str] = re.compile(search_regex_string)
    keys: List[str] = [x for x in w2v.wv.vocab if search_regex.match(x)]
    if not nearest_neighbor_count:
        # adjust the graph size depending on the given parameters to prevent bloating
        nearest_neighbor_count: int = max(int(100 * (min_count ** 2) / (1 + len(keys))), 2)
    keys = [x for x in keys if all(y.isalpha() for y in x) and w2v.wv.vocab[x].count >= min_count]
    edge_color: Tuple[float, float, float] = (0.6, 0.6, 0.6)
    add_edges(keys, w2v, nearest_neighbor_count, min_count, graph)
    pos: dict = nx.spring_layout(graph, k=0.7, iterations=100)
    pyplot.clf()
    pyplot.subplot()
    nx.draw(graph, pos, node_size=25, with_labels=True, alpha=1)
    colors: List[Tuple[float, float, float]] = []
    highlight_regex: Pattern[str] = re.compile(highlight_regex_string)
    for edge in graph.edges:
        if highlight_regex_string and any(highlight_regex.match(x) for x in edge) and any(
                search_regex.match(x) for x in edge):
            colors.append((1, 0, 0))
        else:
            colors.append(edge_color)
    nx.draw_networkx_edges(graph, pos, alpha=1, edge_color=colors)
    pyplot.savefig(fname=Config.NETWORK_GRAPH_TMP_PATH, format="svg", bbox_inches="tight")
    xml_string: str = open(Config.NETWORK_GRAPH_TMP_PATH).read()
    os.remove(Config.NETWORK_GRAPH_TMP_PATH)
    svg_string: str = re.findall(r"<svg[\s\S]*?svg>", xml_string)[0]
    return svg_string
