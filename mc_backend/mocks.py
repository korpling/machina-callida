import json
import logging
import os
import shutil
from collections import OrderedDict
from datetime import datetime
from typing import List, Tuple, Dict
from unittest.mock import patch

from conllu import TokenList
from flask import Flask
from flask.ctx import AppContext
from flask.testing import FlaskClient
from gensim.models import Word2Vec
from gensim.models.keyedvectors import Vocab
from networkx import Graph
from numpy.core.multiarray import ndarray

from mcserver import Config, TestingConfig
from mcserver.app import db, shutdown_session
from mcserver.app.models import Phenomenon, PartOfSpeech, CitationLevel, ExerciseData, GraphData, \
    LinkMC, NodeMC, Language, Dependency, Case, AnnisResponse, Solution, TextPart, Citation, ExerciseMC, CorpusMC, \
    SolutionElement
from mcserver.app.services import AnnotationService, CustomCorpusService, TextService, DatabaseService
from mcserver.models_auto import Corpus, Exercise, UpdateInfo


class MockFilterBy:
    def __init__(self, ui: UpdateInfo = None):
        self.ui: UpdateInfo = ui

    def first(self):
        return self.ui


class MockQuery:
    def __init__(self, ui: UpdateInfo = None):
        self.ui: UpdateInfo = ui

    def all(self):
        # DO NOT MAKE THIS POINT TO THE DATABASE SERVICE, IT WILL BE MOCKED ANYWAY
        return db.session.query(Corpus).all()

    def filter_by(self, **kwargs):
        return MockFilterBy(self.ui)


class MockResponse:
    def __init__(self, text: str, ok: bool = True, content: bytes = b""):
        self.content: bytes = content
        self.encoding: str = "utf-8"
        self.ok: bool = ok
        self.text: str = text

    def raise_for_status(self) -> None:
        pass


class MockWV:
    def __init__(self):
        self.vocab: Dict[str, Vocab] = {"ueritas": Vocab(count=50), "uera": Vocab(count=50)}
        ret_val: ndarray = ndarray((100,))
        ret_val.fill(0.5)
        self.get_vector_return_value: ndarray = ret_val

    def get_vector(self, word: str) -> ndarray:
        return self.get_vector_return_value


class MockW2V:
    def __init__(self):
        self.wv = MockWV()


class TestHelper:
    def __init__(self, app: Flask):
        self.app: Flask = app
        self.app_context: AppContext = self.app.app_context()
        self.client: FlaskClient = self.app.test_client()

    @staticmethod
    def update_flask_app(class_name: str, app_factory: callable) -> None:
        """Sets up and tears down the testing environment for each Test Case."""
        if len(Mocks.app_dict) and list(Mocks.app_dict.keys())[0] != class_name:
            if Config.CORPUS_STORAGE_MANAGER:
                Config.CORPUS_STORAGE_MANAGER.__exit__(None, None, None)
            if os.path.exists(Config.GRAPH_DATABASE_DIR):
                shutil.rmtree(Config.GRAPH_DATABASE_DIR)
            list(Mocks.app_dict.values())[0].app_context.pop()
            shutdown_session()
            db.drop_all()
            Mocks.app_dict = {}
        if not len(Mocks.app_dict):
            with patch.object(TextService, "init_stop_words_latin"):
                Mocks.app_dict[class_name] = TestHelper(app_factory(TestingConfig))
            Mocks.app_dict[class_name].app.logger.setLevel(logging.WARNING)
            Mocks.app_dict[class_name].app.testing = True
        DatabaseService.commit()


class Mocks:
    """This class contains mock objects for unit testing purposes."""
    annotations: List[TokenList] = [TokenList(
        tokens=[{"id": 1, "form": "Caesar", "lemma": "Caeso", "upostag": "VERB", "xpostag": "L3|modJ|tem3|gen4|stAV",
                 "feats": {"Mood": "Ind", "Number": "Sing", "Person": "1", "Tense": "Fut", "VerbForm": "Fin",
                           "Voice": "Pass"}, "head": 0, "deprel": "root", "deps": None, "misc": {"ref": "1.1"}},
                {"id": 2, "form": "et", "lemma": "et", "upostag": "CCONJ", "xpostag": "O4|stRL", "feats": None,
                 "head": 3, "deprel": "cc", "deps": None, "misc": None},
                {"id": 3, "form": "Galli", "lemma": "Gallo", "upostag": "VERB", "xpostag": "L3|modQ|tem1|stAC",
                 "feats": {"Tense": "Pres", "VerbForm": "Inf", "Voice": "Pass"}, "head": 1, "deprel": "conj",
                 "deps": None, "misc": None},
                {"id": 4, "form": "fortes", "lemma": "fors", "upostag": "NOUN", "xpostag": "C1|grn1|casJ|gen2|stRS",
                 "feats": {"Case": "Nom", "Degree": "Pos", "Gender": "Fem", "Number": "Plur"}, "head": 3,
                 "deprel": "nsubj:pass", "deps": None, "misc": None},
                {"id": 5, "form": "sunt", "lemma": "sum", "upostag": "AUX", "xpostag": "N3|modA|tem1|gen9|stAV",
                 "feats": {"Mood": "Ind", "Number": "Plur", "Person": "3", "Tense": "Pres", "VerbForm": "Fin",
                           "Voice": "Act"}, "head": 3, "deprel": "aux:pass", "deps": None,
                 "misc": {"SpaceAfter": "No"}},
                {"id": 6, "form": ".", "lemma": ".", "upostag": "PUNCT", "xpostag": "Punc", "feats": None, "head": 1,
                 "deprel": "punct", "deps": None, "misc": None}],
        metadata=OrderedDict([("sent_id", "1"), ("urn", "urn:cts:latinLit:phi0448.phi001.perseus-lat2:1.1.1-1.1.1")]))]
    annis_response_dict: dict = {"graph_data_raw": {"directed": True, "multigraph": True, "graph": {}, "nodes": [
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok1",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "Pars", "udep::lemma": "pars",
         "udep::upostag": "NOUN", "udep::xpostag": "Nb", "udep::feats": "Case=Nom|Gender=Fem|Number=Sing",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok1"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok3",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "formator", "udep::lemma": "formator",
         "udep::upostag": "NOUN", "udep::xpostag": "Nb", "udep::feats": "Case=Nom|Gender=Masc|Number=Sing",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok3"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok7",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "praecepturus", "udep::lemma": "praecipio",
         "udep::upostag": "VERB", "udep::xpostag": "V-",
         "udep::feats": "Case=Nom|Gender=Masc|Number=Sing|Tense=Fut|VerbForm=Part|Voice=Act",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok7"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok16",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "qui", "udep::lemma": "qvi",
         "udep::upostag": "PRON", "udep::xpostag": "Pr", "udep::feats": "Case=Nom|Gender=Masc|Number=Plur|PronType=Rel",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok16"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok9",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "rhetores", "udep::lemma": "rhetor",
         "udep::upostag": "NOUN", "udep::xpostag": "Nb", "udep::feats": "Case=Acc|Gender=Masc|Number=Plur",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok9"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok2",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "est", "udep::lemma": "sum",
         "udep::upostag": "AUX", "udep::xpostag": "V-",
         "udep::feats": "Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin|Voice=Act",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok2"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok17",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "dum", "udep::lemma": "dum",
         "udep::upostag": "SCONJ", "udep::xpostag": "G-",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok17"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok4",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "agricolae", "udep::lemma": "Agricola",
         "udep::upostag": "NOUN", "udep::xpostag": "Nb", "udep::feats": "Case=Gen|Gender=Masc|Number=Sing",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok4"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok8",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "es", "udep::lemma": "sum",
         "udep::upostag": "AUX", "udep::xpostag": "V-",
         "udep::feats": "Mood=Ind|Number=Sing|Person=2|Tense=Pres|VerbForm=Fin|Voice=Act",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok8"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok12",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "a", "udep::lemma": "ab",
         "udep::upostag": "ADP", "udep::xpostag": "R-",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok12"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok10",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "aemulari", "udep::lemma": "aemulor",
         "udep::upostag": "VERB", "udep::xpostag": "V-", "udep::feats": "Tense=Pres|VerbForm=Inf|Voice=Pass",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok10"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok3",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "prima", "udep::lemma": "primus",
         "udep::upostag": "ADJ", "udep::xpostag": "Mo", "udep::feats": "Case=Nom|Gender=Fem|Number=Sing",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok3"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok13",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "plerisque", "udep::lemma": "plerusque",
         "udep::upostag": "ADJ", "udep::xpostag": "A-", "udep::feats": "Case=Abl|Degree=Pos|Gender=Masc|Number=Plur",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok13"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok18",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "diserte", "udep::lemma": "diserte",
         "udep::upostag": "ADV", "udep::xpostag": "Df", "udep::feats": "Degree=Pos",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok18"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok5",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "debet", "udep::lemma": "debeo",
         "udep::upostag": "VERB", "udep::xpostag": "V-",
         "udep::feats": "Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin|Voice=Act", "udep::deps": "root",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok5"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok9",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "aestimare", "udep::lemma": "aestimo",
         "udep::upostag": "VERB", "udep::xpostag": "V-", "udep::feats": "Tense=Pres|VerbForm=Inf|Voice=Act",
         "udep::deps": "root", "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok9"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok11",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "quod", "udep::lemma": "qui",
         "udep::upostag": "PRON", "udep::xpostag": "Pr", "udep::feats": "Case=Acc|Gender=Neut|Number=Sing|PronType=Rel",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok11"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok14",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "factum", "udep::lemma": "facio",
         "udep::upostag": "VERB", "udep::xpostag": "V-",
         "udep::feats": "Aspect=Perf|Case=Nom|Gender=Neut|Number=Sing|Tense=Past|VerbForm=Part|Voice=Pass",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok14"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok19",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "loquuntur", "udep::lemma": "loquor",
         "udep::upostag": "VERB", "udep::xpostag": "V-",
         "udep::feats": "Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin|Voice=Pass",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok19"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok4",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "prudentiae", "udep::lemma": "prudentia",
         "udep::upostag": "NOUN", "udep::xpostag": "Nb", "udep::feats": "Case=Gen|Gender=Fem|Number=Sing",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok4"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok10",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "personam", "udep::lemma": "persona",
         "udep::upostag": "NOUN", "udep::xpostag": "Nb", "udep::feats": "Case=Acc|Gender=Fem|Number=Sing",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok10"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok6",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "artibus", "udep::lemma": "ars",
         "udep::upostag": "NOUN", "udep::xpostag": "Nb", "udep::feats": "Case=Abl|Gender=Fem|Number=Plur",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok6"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok15",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "est", "udep::lemma": "sum",
         "udep::upostag": "AUX", "udep::xpostag": "V-",
         "udep::feats": "Mood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin|Voice=Act",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok15"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok7",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "et", "udep::lemma": "et",
         "udep::upostag": "CCONJ", "udep::xpostag": "C-",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok7"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok20",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "rusticis", "udep::lemma": "rusticus",
         "udep::upostag": "ADJ", "udep::xpostag": "A-", "udep::feats": "Case=Abl|Degree=Pos|Gender=Masc|Number=Plur",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok20"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok11",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": ".", "udep::lemma": ".",
         "udep::upostag": "PUNCT", "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok11"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok5",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "ipsam", "udep::lemma": "ipse",
         "udep::upostag": "DET", "udep::xpostag": "Pd", "udep::feats": "Case=Acc|Gender=Fem|Number=Sing",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok5"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok8",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "eloquentia", "udep::lemma": "eloquentia",
         "udep::upostag": "NOUN", "udep::xpostag": "Nb", "udep::feats": "Case=Abl|Gender=Fem|Number=Sing",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok8"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok22",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "sunt", "udep::lemma": "sum",
         "udep::upostag": "AUX", "udep::xpostag": "V-",
         "udep::feats": "Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin|Voice=Act",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok22"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok21",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "adsecuti", "udep::lemma": "assequor",
         "udep::upostag": "VERB", "udep::xpostag": "V-",
         "udep::feats": "Aspect=Perf|Case=Nom|Gender=Masc|Number=Plur|Tense=Past|VerbForm=Part|Voice=Pass",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok21"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok1",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "Neque", "udep::lemma": "neque",
         "udep::upostag": "ADV", "udep::xpostag": "Df",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok1"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok6",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "cui", "udep::lemma": "qui",
         "udep::upostag": "PRON", "udep::xpostag": "Pr", "udep::feats": "Case=Dat|Gender=Fem|Number=Sing|PronType=Rel",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok6"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok4",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "praefationis", "udep::lemma": "praefatio",
         "udep::upostag": "NOUN", "udep::xpostag": "Nb", "udep::feats": "Case=Gen|Gender=Fem|Number=Sing",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok4"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok23",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "ut", "udep::lemma": "ut",
         "udep::upostag": "SCONJ", "udep::xpostag": "G-",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok23"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok2",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "enim", "udep::lemma": "enim",
         "udep::upostag": "ADV", "udep::xpostag": "Df",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok2"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok1",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "Sed", "udep::lemma": "sed",
         "udep::upostag": "CCONJ", "udep::xpostag": "C-",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok1"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok25",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "doctrina", "udep::lemma": "doctrina",
         "udep::upostag": "NOUN", "udep::xpostag": "Nb", "udep::feats": "Case=Nom|Gender=Fem|Number=Sing",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok25"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok24",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "eorum", "udep::lemma": "is",
         "udep::upostag": "PRON", "udep::xpostag": "Pp",
         "udep::feats": "Case=Gen|Gender=Masc|Number=Plur|Person=3|PronType=Prs",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok24"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok5",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "moram", "udep::lemma": "mora",
         "udep::upostag": "NOUN", "udep::xpostag": "Nb", "udep::feats": "Case=Acc|Gender=Fem|Number=Sing",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok5"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok2",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "nos", "udep::lemma": "nos",
         "udep::upostag": "PRON", "udep::xpostag": "Pp",
         "udep::feats": "Case=Nom|Gender=Masc|Number=Plur|Person=1|PronType=Prs",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok2"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok7",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "quos", "udep::lemma": "qui",
         "udep::upostag": "PRON", "udep::xpostag": "Pr", "udep::feats": "Case=Acc|Gender=Masc|Number=Plur|PronType=Rel",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok7"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok26",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "nec", "udep::lemma": "neque",
         "udep::upostag": "ADV", "udep::xpostag": "Df",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok26"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok27",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "a", "udep::lemma": "ab",
         "udep::upostag": "ADP", "udep::xpostag": "R-",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok27"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok6",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "ne", "udep::lemma": "ne",
         "udep::upostag": "SCONJ", "udep::xpostag": "G-",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok6"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok3",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "recidamus", "udep::lemma": "recido#2",
         "udep::upostag": "VERB", "udep::xpostag": "V-",
         "udep::feats": "Mood=Sub|Number=Plur|Person=1|Tense=Pres|VerbForm=Fin|Voice=Act", "udep::deps": "root",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok3"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok8",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "reprehendimus",
         "udep::lemma": "repr(eh)endo", "udep::upostag": "VERB", "udep::xpostag": "V-",
         "udep::feats": "Mood=Ind|Number=Plur|Person=1|Tense=Pres|VerbForm=Fin|Voice=Act",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok8"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok30",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "intelligi", "udep::lemma": "intellego",
         "udep::upostag": "VERB", "udep::xpostag": "V-", "udep::feats": "Tense=Pres|VerbForm=Inf|Voice=Pass",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok30"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok28",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "disertissimis", "udep::lemma": "dissero",
         "udep::upostag": "ADJ", "udep::xpostag": "A-", "udep::feats": "Case=Abl|Degree=Sup|Gender=Masc|Number=Plur",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok28"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok31",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": ".", "udep::lemma": ".",
         "udep::upostag": "PUNCT", "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok31"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok9",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "imitemur", "udep::lemma": "imitor",
         "udep::upostag": "VERB", "udep::xpostag": "V-",
         "udep::feats": "Mood=Sub|Number=Plur|Person=1|Tense=Pres|VerbForm=Fin|Voice=Pass",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok9"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok10",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": ".", "udep::lemma": ".",
         "udep::upostag": "PUNCT", "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok10"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok29",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "possit", "udep::lemma": "possum",
         "udep::upostag": "VERB", "udep::xpostag": "V-",
         "udep::feats": "Mood=Sub|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin|Voice=Act",
         "id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok29"},
        {"annis::node_name": "urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok30",
         "annis::node_type": "node", "annis::type": "node", "annis::tok": "possit", "udep::lemma": "possum",
         "udep::upostag": "VERB", "udep::xpostag": "V-",
         "udep::feats": "Mood=Sub|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin|Voice=Act",
         "id": 1}
    ], "links": [
        {"udep::deprel": "nmod", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok1",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok3", "key": 0},
        {"udep::deprel": "nmod", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok1",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok4", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok1",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok2", "key": 0},
        {"udep::deprel": "nmod", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok3",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok4", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok3",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok4", "key": 1},
        {"udep::deprel": "iobj", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok7",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok6", "key": 0},
        {"udep::deprel": "aux", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok7",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok8", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok7",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok8", "key": 1},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok16",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok17", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok9",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok10", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok2",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok3", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok17",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok18", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok4",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok5", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok8",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok9", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok12",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok13", "key": 0},
        {"udep::deprel": "obl", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok10",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok6", "key": 0},
        {"udep::deprel": "obj:dir", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok10",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok9", "key": 0},
        {"udep::deprel": "advcl", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok10",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok14", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok10",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok11", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok3",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok4", "key": 0},
        {"udep::deprel": "case", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok13",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok12", "key": 0},
        {"udep::deprel": "advcl", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok13",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok21", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok13",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok14", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok18",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok19", "key": 0},
        {"udep::deprel": "advmod", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok5",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok1", "key": 0},
        {"udep::deprel": "discourse", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok5",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok2", "key": 0},
        {"udep::deprel": "nsubj", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok5",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok3", "key": 0},
        {"udep::deprel": "xcomp", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok5",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok10", "key": 0},
        {"annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok5",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok31", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok5",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok6", "key": 0},
        {"udep::deprel": "nsubj", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok9",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok1", "key": 0},
        {"udep::deprel": "cop", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok9",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok2", "key": 0},
        {"udep::deprel": "obj:dir", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok9",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok10", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok9",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok10", "key": 1},
        {"annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok9",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok11", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok11",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok12", "key": 0},
        {"udep::deprel": "nsubj:pass", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok14",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok11", "key": 0},
        {"udep::deprel": "obl:agent", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok14",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok13", "key": 0},
        {"udep::deprel": "aux:pass", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok14",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok15", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok14",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok15", "key": 1},
        {"udep::deprel": "mark", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok19",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok17", "key": 0},
        {"udep::deprel": "advmod", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok19",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok18", "key": 0},
        {"udep::deprel": "iobj", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok19",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok20", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok19",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok20", "key": 1},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok4",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok5", "key": 0},
        {"udep::deprel": "det", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok10",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok5", "key": 0},
        {"udep::deprel": "acl", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok10",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok7", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok10",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok11", "key": 0},
        {"udep::deprel": "cc", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok6",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok7", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok6",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok7", "key": 1},
        {"udep::deprel": "conj", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok6",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok8", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok15",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok16", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok7",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok8", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok20",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok21", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok11",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok1", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok5",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok6", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok8",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok9", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok22",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok23", "key": 0},
        {"udep::deprel": "nsubj", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok21",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok16", "key": 0},
        {"udep::deprel": "advcl", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok21",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok19", "key": 0},
        {"udep::deprel": "aux", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok21",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok22", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok21",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok22", "key": 1},
        {"udep::deprel": "advcl", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok21",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok29", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok1",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok2", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok6",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok7", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok4",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok5", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok23",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok24", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok2",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok3", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok1",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok2", "key": 0},
        {"udep::deprel": "det", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok25",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok24", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok25",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok26", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok24",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok25", "key": 0},
        {"udep::deprel": "nmod", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok5",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok4", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok5",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok6", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok2",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok3", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok7",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok8", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok26",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok27", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok27",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok28", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok6",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok7", "key": 0},
        {"udep::deprel": "cc", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok3",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok1", "key": 0},
        {"udep::deprel": "nsubj", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok3",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok2", "key": 0},
        {"udep::deprel": "obj:dir", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok3",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok5", "key": 0},
        {"udep::deprel": "advcl", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok3",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok9", "key": 0},
        {"annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok3",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok10", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok3",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok4", "key": 0},
        {"udep::deprel": "obj:dir", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok8",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok7", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok8",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok9", "key": 0},
        {"udep::deprel": "obl:agent", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok30",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok28", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok30",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok31", "key": 0},
        {"udep::deprel": "case", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok28",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok27", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok28",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok29", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok31",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok1", "key": 0},
        {"udep::deprel": "mark", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok9",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok6", "key": 0},
        {"udep::deprel": "obj:dir", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok9",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok8", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok9",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok10", "key": 0},
        {"udep::deprel": "mark", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok29",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok23", "key": 0},
        {"udep::deprel": "nsubj", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok29",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok25", "key": 0},
        {"udep::deprel": "advmod", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok29",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok26", "key": 0},
        {"udep::deprel": "xcomp", "annis::component_name": "dep", "annis::component_type": "Pointing",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok29",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok30", "key": 0},
        {"annis::component_name": "", "annis::component_type": "Ordering",
         "source": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok29",
         "target": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok30", "key": 1}]},
                                 "solutions": [{"target": {"sentence_id": 159692, "token_id": 7,
                                                           "salt_id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok7",
                                                           "content": "praecepturus"},
                                                "value": {"sentence_id": 0, "token_id": 0, "content": "",
                                                          "salt_id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok1"}},
                                               {
                                                   "target": {"sentence_id": 159692, "token_id": 9,
                                                              "salt_id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok9",
                                                              "content": "aestimare"},
                                                   "value": {"sentence_id": 0, "token_id": 0, "content": "",
                                                             "salt_id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok1"}},
                                               {
                                                   "target": {"sentence_id": 159693, "token_id": 5,
                                                              "salt_id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159693tok5",
                                                              "content": "debet"},
                                                   "value": {"sentence_id": 0, "token_id": 0, "content": "",
                                                             "salt_id": "salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok1"}}],
                                 "conll": "# newdoc id = /var/folders/30/yqnv6lz56r14dqhpw18knn2r0000gp/T/tmp7qn86au9\n# sent_id = 1\n# text = Caesar fortis est.\n1\tCaesar\tCaeso\tVERB\tC1|grn1|casA|gen1|stAN\tCase=Nom|Degree=Pos|Gender=Masc|Number=Sing\t2\tcsubj\t_\t_\n2\tfortis\tfortis\tADJ\tC1|grn1|casA|gen1|stAN\tCase=Nom|Degree=Pos|Gender=Masc|Number=Sing\t0\troot\troot\t_\n3\test\tsum\tAUX\tN3|modA|tem1|gen6|stAV\tMood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin|Voice=Act\t2\tcop\t_\tSpaceAfter=No\n4\t.\t.\tPUNCT\tPunc\t_\t2\tpunct\t_\t_\n\n# sent_id = 2\n# text = Galli moriuntur.\n1\tGalli\tGallus\tPRON\tF1|grn1|casJ|gen1|stPD\tCase=Nom|Degree=Pos|Gender=Masc|Number=Plur|PronType=Dem\t2\tnsubj:pass\t_\t_\n2\tmoriuntur\tmorior\tVERB\tL3|modJ|tem1|gen9|stAV\tMood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin|Voice=Pass\t0\troot\troot\tSpaceAfter=No\n3\t.\t.\tPUNCT\tPunc\t_\t2\tpunct\t_\tSpacesAfter=\\n\n\n"}
    app_dict: Dict[str, TestHelper] = {}
    aqls: List[str] = ["=".join([Phenomenon.UPOSTAG, '"{0}"'.format(
        AnnotationService.phenomenon_map[Phenomenon.UPOSTAG][PartOfSpeech.verb.name][0])])]
    graph_data: GraphData = AnnotationService.map_graph_data(annis_response_dict["graph_data_raw"])
    annis_response: AnnisResponse = AnnisResponse(graph_data=graph_data)
    corpora: List[Corpus] = [
        CorpusMC.from_dict(title="title1", source_urn="urn1", author="author1",
                           citation_level_1=CitationLevel.default.value),
        CorpusMC.from_dict(title="title2", source_urn="urn2", author="author2",
                           citation_level_1=CitationLevel.default.value)]
    cts_capabilities_xml: str = '<GetCapabilities xmlns="http://chs.harvard.edu/xmlns/cts"><request><requestName>GetInventory</requestName><requestFilters>urn=urn:cts:latinLit</requestFilters></request><reply><ti:TextInventory xmlns:ti=\'http://chs.harvard.edu/xmlns/cts\'><ti:textgroup urn=\'urn:cts:latinLit:phi0660\' xmlns:ti=\'http://chs.harvard.edu/xmlns/cts\'><ti:groupname xml:lang=\'eng\'>Tibullus</ti:groupname><ti:groupname xml:lang=\'lat\'>Corpus Tibullianum</ti:groupname><ti:work xml:lang="lat" urn=\'urn:cts:latinLit:phi0660.phi001\' groupUrn=\'urn:cts:latinLit:phi0660\' xmlns:ti=\'http://chs.harvard.edu/xmlns/cts\'><ti:title xml:lang=\'lat\'>Elegiae</ti:title><ti:edition urn=\'urn:cts:latinLit:phi0660.phi001.perseus-lat2\' workUrn=\'urn:cts:latinLit:phi0660.phi001\' xmlns:ti=\'http://chs.harvard.edu/xmlns/cts\'><ti:label xml:lang=\'eng\'>Elegiae, Aliorumque carminum libri tres</ti:label><ti:description xml:lang=\'eng\'>Tibullus, creator; Postgate, J. P. (John Percival), 1853- 1926, editor </ti:description><ti:online><ti:citationMapping><ti:citation label="book" xpath="/tei:div[@n=\'?\']" scope="/tei:TEI/tei:text/tei:body/tei:div"><ti:citation label="poem" xpath="/tei:div[@n=\'?\']" scope="/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n=\'?\']"><ti:citation label="line" xpath="//tei:l[@n=\'?\']" scope="/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n=\'?\']/tei:div[@n=\'?\']"></ti:citation></ti:citation></ti:citation></ti:citationMapping></ti:online></ti:edition></ti:work><ti:work xml:lang="lat" urn=\'urn:cts:latinLit:phi0660.phi003\' groupUrn=\'urn:cts:latinLit:phi0660\' xmlns:ti=\'http://chs.harvard.edu/xmlns/cts\'> </ti:work></ti:textgroup></ti:TextInventory></reply></GetCapabilities>'
    cts_passage_xml: str = '<GetPassage xmlns:tei="http://www.tei-c.org/ns/1.0" xmlns="http://chs.harvard.edu/xmlns/cts"><request><requestName>GetPassage</requestName><requestUrn>urn:cts:latinLit:phi0448.phi001.perseus-lat2:1.1.1-1.1.2</requestUrn></request><reply><urn>urn:cts:latinLit:phi0448.phi001.perseus-lat2:1.1.1-1.1.2</urn><passage><TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body><div type="edition" xml:lang="lat" n="urn:cts:latinLit:phi0448.phi001.perseus-lat2"><div n="1" type="textpart" subtype="book"><div type="textpart" subtype="chapter" n="1"><div type="textpart" subtype="section" n="1"><p>Gallia est omnis divisa in partes tres, quarum unam incolunt Belgae, aliam Aquitani, tertiam qui ipsorum lingua Celtae, nostra Galli appellantur.</p></div><div type="textpart" subtype="section" n="2"><p>Hi omnes lingua, institutis, legibus inter se differunt. Gallos ab Aquitanis Garumna flumen, a Belgis Matrona et Sequana dividit.</p></div></div></div></div></body></text></TEI></passage></reply></GetPassage>'
    cts_passage_xml_1_level: str = '<GetPassage xmlns:tei="http://www.tei-c.org/ns/1.0" xmlns="http://chs.harvard.edu/xmlns/cts"><request><requestName>GetPassage</requestName><requestUrn>urn:cts:latinLit:phi0448.phi001.perseus-lat2:1.1-1.2</requestUrn></request><reply><urn>urn:cts:latinLit:phi0448.phi001.perseus-lat2:1.1-1.2</urn><passage><TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body><div type="edition" xml:lang="lat" n="urn:cts:latinLit:phi0448.phi001.perseus-lat2"><div n="1" type="textpart" subtype="book"><p>Gallia est omnis divisa in partes tres, quarum unam incolunt Belgae, aliam Aquitani, tertiam qui ipsorum lingua Celtae, nostra Galli appellantur.</p></div><div n="2" type="textpart" subtype="book"><p>Gallia est omnis divisa in partes tres, quarum unam incolunt Belgae, aliam Aquitani, tertiam qui ipsorum lingua Celtae, nostra Galli appellantur.</p></div><div n="3" type="textpart" subtype="book"><p>Gallia est omnis divisa in partes tres, quarum unam incolunt Belgae, aliam Aquitani, tertiam qui ipsorum lingua Celtae, nostra Galli appellantur.</p></div></div></body></text></TEI></passage></reply></GetPassage>'
    cts_passage_xml_2_levels: str = '<GetPassage xmlns:tei="http://www.tei-c.org/ns/1.0" xmlns="http://chs.harvard.edu/xmlns/cts"><request><requestName>GetPassage</requestName><requestUrn>urn:cts:latinLit:phi0448.phi001.perseus-lat2:1.1-1.2</requestUrn></request><reply><urn>urn:cts:latinLit:phi0448.phi001.perseus-lat2:1.1-1.2</urn><passage><TEI xmlns="http://www.tei-c.org/ns/1.0"><text><body><div type="edition" xml:lang="lat" n="urn:cts:latinLit:phi0448.phi001.perseus-lat2"><div n="1" type="textpart" subtype="book"><div type="textpart" subtype="section" n="1"><p>Gallia est omnis divisa in partes tres, quarum unam incolunt Belgae, aliam Aquitani, tertiam qui ipsorum lingua Celtae, nostra Galli appellantur.</p></div></div></div></body></text></TEI></passage></reply></GetPassage>'
    cts_reff_xml: str = '<GetValidReff xmlns:tei="http://www.tei-c.org/ns/1.0" xmlns="http://chs.harvard.edu/xmlns/cts"><request><requestName>GetValidReff</requestName><requestUrn>urn:cts:latinLit:phi0448.phi001.perseus-lat2:1.1</requestUrn><requestLevel>3</requestLevel></request><reply><reff><urn>urn:cts:latinLit:phi0448.phi001.perseus-lat2:1.1.1</urn><urn>urn:cts:latinLit:phi0448.phi001.perseus-lat2:1.1.2</urn><urn>urn:cts:latinLit:phi0448.phi001.perseus-lat2:1.1.3</urn><urn>urn:cts:latinLit:phi0448.phi001.perseus-lat2:1.1.4</urn><urn>urn:cts:latinLit:phi0448.phi001.perseus-lat2:1.1.5</urn><urn>urn:cts:latinLit:phi0448.phi001.perseus-lat2:1.1.6</urn><urn>urn:cts:latinLit:phi0448.phi001.perseus-lat2:1.1.7</urn></reff></reply></GetValidReff>'
    exercise: Exercise = ExerciseMC.from_dict(
        eid="test", last_access_time=datetime.utcnow().timestamp(), exercise_type='ddwtos',
        search_values=f'["{Phenomenon.FEATS}={Case.accusative.name}", "{Phenomenon.DEPENDENCY}={Dependency.object.name}", "{Phenomenon.LEMMA}=bellum", "{Phenomenon.DEPENDENCY}={Dependency.root.name}"]',
        language=Language.English.value,
        conll="# newdoc id = /var/folders/30/yqnv6lz56r14dqhpw18knn2r0000gp/T/tmp7qn86au9\n# newpar\n# sent_id = 1\n# text = Caesar fortis est.\n1\tCaesar\tCaeso\tVERB\tC1|grn1|casA|gen1|stAN\tCase=Nom|Degree=Pos|Gender=Masc|Number=Sing\t2\tcsubj\t_\t_\n2\tfortis\tfortis\tADJ\tC1|grn1|casA|gen1|stAN\tCase=Nom|Degree=Pos|Gender=Masc|Number=Sing\t0\troot\t_\t_\n3\test\tsum\tAUX\tN3|modA|tem1|gen6|stAV\tMood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin|Voice=Act\t2\tcop\t_\tSpaceAfter=No\n4\t.\t.\tPUNCT\tPunc\t_\t2\tpunct\t_\t_\n\n# sent_id = 2\n# text = Galli moriuntur.\n1\tGalli\tGallus\tPRON\tF1|grn1|casJ|gen1|stPD\tCase=Nom|Degree=Pos|Gender=Masc|Number=Plur|PronType=Dem\t2\tnsubj:pass\t_\t_\n2\tmoriuntur\tmorior\tVERB\tL3|modJ|tem1|gen9|stAV\tMood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin|Voice=Pass\t0\troot\t_\tSpaceAfter=No\n3\t.\t.\tPUNCT\tPunc\t_\t2\tpunct\t_\tSpacesAfter=\\n\n\n",
        solutions=json.dumps([
            Solution(target=SolutionElement(
                sentence_id=1, token_id=1, content="praecepturus",
                salt_id="salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent1tok1"),
                value=SolutionElement(
                    sentence_id=1, token_id=2, content="Caesar",
                    salt_id="salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent1tok2")).to_dict()
        ]).replace(" ", ""),
        urn=f"{CustomCorpusService.custom_corpora[4].corpus.source_urn}:2.23.1-2.23.1")
    exercise_data: ExerciseData = ExerciseData(
        graph=GraphData(directed=False, graph={}, links=[
            LinkMC(annis_component_name=Config.GRAPHANNIS_DEPENDENCY_LINK, annis_component_type="act",
                   source="doc1#sent1tok1", target="doc1#sent1tok2", udep_deprel="uddr")],
                        multigraph=False, nodes=[
                NodeMC(annis_node_name="ann", annis_node_type="ant", annis_tok="atk", annis_type="atp",
                       id="doc1#sent1tok1", udep_upostag="udupt", udep_xpostag="udxpt", udep_feats="udf",
                       udep_lemma="udl"),
                NodeMC(annis_node_name="ann", annis_node_type="ant", annis_tok="atk", annis_type="atp",
                       id="doc1#sent1tok2", udep_upostag="udupt", udep_xpostag="udxpt", udep_feats="udf",
                       udep_lemma="udl")]), uri="/test", solutions=[])
    exercise_pdf: bytes = b'%PDF-1.4\n%\x93\x8c\x8b\x9e ReportLab Generated PDF document http://www.reportlab.com\n1 0 obj\n<<\n/F1 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/BaseFont /Helvetica /Encoding /WinAnsiEncoding /Name /F1 /Subtype /Type1 /Type /Font\n>>\nendobj\n3 0 obj\n<<\n/BitsPerComponent 1 /ColorSpace /DeviceGray /Filter [ /ASCII85Decode ] /Height 23 /Length 223 /Subtype /Image \n  /Type /XObject /Width 24\n>>\nstream\n\n            003B00 002700 002480 0E4940 114920 14B220 3CB650\n            75FE88 17FF8C 175F14 1C07E2 3803C4 703182 F8EDFC\n            B2BBC2 BB6F84 31BFC2 18EA3C 0E3E00 07FC00 03F800\n            1E1800 1FF800>\n            endstream\nendobj\n4 0 obj\n<<\n/Contents 8 0 R /MediaBox [ 0 0 595.2756 841.8898 ] /Parent 7 0 R /Resources <<\n/Font 1 0 R /ProcSet [ /PDF /Text /ImageB /ImageC /ImageI ] /XObject <<\n/FormXob.c7485dcc8d256a6f197ed7802687f252 3 0 R\n>>\n>> /Rotate 0 /Trans <<\n\n>> \n  /Type /Page\n>>\nendobj\n5 0 obj\n<<\n/PageMode /UseNone /Pages 7 0 R /Type /Catalog\n>>\nendobj\n6 0 obj\n<<\n/Author () /CreationDate'
    exercise_xml: str = '<quiz>   <question type="matching">       <name>           <text></text>       </name>       <questiontext format="html">           <text><![CDATA[<br><p></p><p></p><br><br>]]></text>       </questiontext>       <generalfeedback format="html">           <text></text>       </generalfeedback>       <defaultgrade>1.0000000</defaultgrade>       <penalty>0.1000000</penalty>       <hidden>0</hidden>       <shuffleanswers>1</shuffleanswers>       <correctfeedback format="html">           <text></text>       </correctfeedback>       <partiallycorrectfeedback format="html">           <text></text>       </partiallycorrectfeedback>       <incorrectfeedback format="html">           <text></text>       </incorrectfeedback>       <shownumcorrect/>              <tags></tags>   </question></quiz>'
    graph_data_raw_part: str = '{"directed":true,"multigraph":true,"graph":{},"nodes":[{"annis::node_name":"'
    h5p_json_cloze: str = '{"textField":"*Caesar* fortis est. Galli moriuntur."}'
    h5p_json_matching: str = '{"textField":"praecepturus *Caesar*\\n"}'
    h5p_json_fill_blanks_1: Tuple[str, str] = ("1_en",
                                               '{"questions": [ "<p>Gaius --> *C.* --> *make*<\/p>", "<p>scribo --> *scribere* --> *write*<\/p>", "<p>commoveri --> *commovere* --> *move / unsettle*<\/p>", "<p>gaudeas --> *gaudere* --> *rejoice / be glad*<\/p>" ], "showSolutions": "Show solutions", "tryAgain": "Try again", "text": "<p><b>Vocabulary knowledge<\/b><br>Fill in the basic form and give a translation of this form.</p>\\n"}')
    h5p_json_fill_blanks_3: Tuple[str, str] = ("3_en",
                                               '{"questions": [ "<p>signum --> *sign*<\/p>", "<p>vas --> *jar*<\/p>", "<p>condicio --> *condition / requirement / term*<\/p>", "<p>clarus --> *clear / bright*<\/p>" ], "showSolutions": "Show solutions", "tryAgain": "Try again", "text": "<p>Translate this word of origin:<\/p>\\n"}')
    h5p_json_fill_blanks_4: Tuple[str, str] = ("4_en",
                                               '{"questions": [ "<p>deducere --> *de*-*ducere* --> *lead away*<\/p>", "<p>commovere --> *com / cum*-*movere* --> *move / to move*<\/p>", "<p>praeclarus --> *prae*-*clarus* --> *highly famous / famous*" ], "showSolutions": "Show solutions", "tryAgain": "Try again", "text": "<p>Break down the compounds into their components and give a possible English translation:<\/p>\\n"}')
    h5p_json_fill_blanks_13: Tuple[str, str] = ("13_en",
                                                '{"questions": [ "<p>Name the Latin phrase for \\"your efficiency\\".<br> *istam virtutem*<\/p>", "<p>Which English word corresponds to the Latin combination of words \\"moderationem animi\\"?<br> *serenity / the serenity / your serenity*<\/p>", "<p>Who sees and hears of the efficiency of Quintus? Indicate the appropriate genitive attributes.<br> *clarissimae provinciae* and *omnium gentium ac nationum*<\/p>" ], "showSolutions": "Show solutions", "tryAgain": "Try again", "text": "<p><b><i>Quid autem reperiri tam eximium aut tam expetendum potest quam istam virtutem, moderationem animi, temperantiam [...] in luce Asiae, in oculis clarissimae provinciae atque in auribus omnium gentium ac nationum esse positam?<\/i><\/b><\/p><br><p>But what can turn out to be greater and more desirable than that your efficiency, your serenity and your modesty [...] were spread out in the public of the province of Asia, before the eyes of the highly famous province and before the ears of all tribes and peoples?<\/p>\\n"}')
    h5p_json_multi_choice: str = '{"answers":[{"correct":false,"text":"<div>He is satisfied.<\/div>\\n","tipsAndFeedback":{"tip":"","chosenFeedback":"","notChosenFeedback":""}},{"correct":true,"text":"<div>It is enough.<\/div>\\n","tipsAndFeedback":{"tip":"","chosenFeedback":"","notChosenFeedback":""}},{"correct":false,"text":"<div>He has enough.<\/div>\\n","tipsAndFeedback":{"tip":"","chosenFeedback":"","notChosenFeedback":""}}],"question":"<p>Choose the correct meaning:<\/p><p><em>satis est.<\/em><\/p>\\n"}'
    h5p_json_multi_choice_2: str = '{"answers":[{"correct":true,"text":"<div>provincia</div>\\n","tipsAndFeedback":{"tip":"","chosenFeedback":"","notChosenFeedback":""}},{"correct":true,"text":"<div>civis</div>\\n","tipsAndFeedback":{"tip":"","chosenFeedback":"","notChosenFeedback":""}},{"correct":true,"text":"<div>socius</div>\\n","tipsAndFeedback":{"tip":"","chosenFeedback":"","notChosenFeedback":""}},{"correct":true,"text":"<div>publicus</div>\\n","tipsAndFeedback":{"tip":"","chosenFeedback":"","notChosenFeedback":""}},{"correct":false,"text":"<div>adventus</div>\\n","tipsAndFeedback":{"tip":"","chosenFeedback":"","notChosenFeedback":""}},{"correct":false,"text":"<div>omnis</div>\\n","tipsAndFeedback":{"tip":"","chosenFeedback":"","notChosenFeedback":""}},{"correct":false,"text":"<div>autem</div>\\n","tipsAndFeedback":{"tip":"","chosenFeedback":"","notChosenFeedback":""}},{"correct":false,"text":"<div>res</div>\\n","tipsAndFeedback":{"tip":"","chosenFeedback":"","notChosenFeedback":""}}],"question":"<p>Choose words (4) that belong to the word field <b>government</b>:</p>\\n"}'
    h5p_json_multi_choice_9: Tuple[str, str] = ("9_en",
                                                '{"answers": [ { "correct": true, "text": "<div>provincia<\/div>\\n", "tipsAndFeedback": { "tip": "", "chosenFeedback": "", "notChosenFeedback": "" } }, { "correct": true, "text": "<div>civis<\/div>\\n", "tipsAndFeedback": { "tip": "", "chosenFeedback": "", "notChosenFeedback": "" } }, { "correct": true, "text": "<div>socius<\/div>\\n", "tipsAndFeedback": { "tip": "", "chosenFeedback": "", "notChosenFeedback": "" } }, { "correct": true, "text": "<div>publicus<\/div>\\n", "tipsAndFeedback": { "tip": "", "chosenFeedback": "", "notChosenFeedback": "" } }, { "correct": false, "text": "<div>adventus<\/div>\\n", "tipsAndFeedback": { "tip": "", "chosenFeedback": "", "notChosenFeedback": "" } }, { "correct": false, "text": "<div>omnis<\/div>\\n", "tipsAndFeedback": { "tip": "", "chosenFeedback": "", "notChosenFeedback": "" } }, { "correct": false, "text": "<div>autem<\/div>\\n", "tipsAndFeedback": { "tip": "", "chosenFeedback": "", "notChosenFeedback": "" } }, { "correct": false, "text": "<div>res<\/div>\\n", "tipsAndFeedback": { "tip": "", "chosenFeedback": "", "notChosenFeedback": "" } } ], "question": "<p>Choose words (4) that belong to the word field <b>government</b>:<\/p>\\n"}')
    h5p_json_voc_list: str = '{"questions":["<p><h4>atque </h4> *and : and*</p>"]}'
    headers_form_data: dict = {"Content-Type": "application/x-www-form-urlencoded"}
    kwic_svg: bytes = b'"<svg height=\\"360\\" id=\\"svg1\\" width=\\"1252\\">'
    nodes: List[dict] = [{"annis::node_name": "urn:cts:latinLit:phi0448.phi001.perseus-lat2:1.1.1-1.1.1/doc1#sent1tok1",
                          "annis::node_type": "node", "annis::type": "node", "annis::tok": "Caesar",
                          "udep::upostag": "VERB", "udep::xpostag": "L3|modJ|tem3|gen4|stAV",
                          "udep::feats": "Mood=Ind|Number=Sing|Person=1|Tense=Fut|VerbForm=Fin|Voice=Pass",
                          "id": "salt:/urn:cts:latinLit:phi0448.phi001.perseus-lat2:1.1.1-1.1.1/doc1#sent1tok1"},
                         {"annis::node_name": "urn:cts:latinLit:phi0448.phi001.perseus-lat2:1.1.1-1.1.1/doc1#sent1tok5",
                          "annis::node_type": "node", "annis::type": "node", "annis::tok": "sunt",
                          "udep::upostag": "AUX", "udep::xpostag": "N3|modA|tem1|gen9|stAV",
                          "udep::feats": "Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin|Voice=Act",
                          "id": "salt:/urn:cts:latinLit:phi0448.phi001.perseus-lat2:1.1.1-1.1.1/doc1#sent1tok5"},
                         {"annis::node_name": "urn:cts:latinLit:phi0448.phi001.perseus-lat2:1.1.1-1.1.1/doc1#sent1tok4",
                          "annis::node_type": "node", "annis::type": "node", "annis::tok": "fortes",
                          "udep::upostag": "NOUN", "udep::xpostag": "C1|grn1|casJ|gen2|stRS",
                          "udep::feats": "Case=Nom|Degree=Pos|Gender=Fem|Number=Plur",
                          "id": "salt:/urn:cts:latinLit:phi0448.phi001.perseus-lat2:1.1.1-1.1.1/doc1#sent1tok4"},
                         {"annis::node_name": "urn:cts:latinLit:phi0448.phi001.perseus-lat2:1.1.1-1.1.1/doc1#sent1tok2",
                          "annis::node_type": "node", "annis::type": "node", "annis::tok": "et",
                          "udep::upostag": "CCONJ", "udep::xpostag": "O4|stRL",
                          "id": "salt:/urn:cts:latinLit:phi0448.phi001.perseus-lat2:1.1.1-1.1.1/doc1#sent1tok2"},
                         {"annis::node_name": "urn:cts:latinLit:phi0448.phi001.perseus-lat2:1.1.1-1.1.1/doc1#sent1tok6",
                          "annis::node_type": "node", "annis::type": "node", "annis::tok": ".",
                          "udep::upostag": "PUNCT", "udep::xpostag": "Punc",
                          "id": "salt:/urn:cts:latinLit:phi0448.phi001.perseus-lat2:1.1.1-1.1.1/doc1#sent1tok6"},
                         {"annis::node_name": "urn:cts:latinLit:phi0448.phi001.perseus-lat2:1.1.1-1.1.1/doc1#sent1tok3",
                          "annis::node_type": "node", "annis::type": "node", "annis::tok": "Galli",
                          "udep::upostag": "VERB", "udep::xpostag": "L3|modQ|tem1|stAC",
                          "udep::feats": "Tense=Pres|VerbForm=Inf|Voice=Pass",
                          "id": "salt:/urn:cts:latinLit:phi0448.phi001.perseus-lat2:1.1.1-1.1.1/doc1#sent1tok3"}]
    proper_nouns: List[str] = ['Alcibiades', 'Carthago', 'Gallia', 'Graecus', 'Hermes', 'Iuppiter', 'Maria', 'Pollux',
                               'Romanus', 'Solomon', 'amor']
    raw_text: str = "Caesar fortis est. Galli moriuntur."
    static_exercises_udpipe_string: str = "1\tscribere\tscribere\n1\tcommovere\tcommovere\n1\tC\tC\n1\tgaudere\tgaudere\n1\tsignum\tsignum\n1\tvas\tvas\n1\tclarus\tclarus\n1\tcondicio\tcondicio\n1\tcom\tcum\n1\tprae\tprae\n1\tmovere\tmovere\n1\tducere\tducere\n1\tde\tde\n1\tcum\tcum\n1\tistam\tiste\n1\tnationum\tnatio\n1\tclarissimae\tclarus\n1\tmoderationem\tmoderatio\n1\tanimi\tanimus\n1\tomnium\tomnis\n1\tgentium\tgens\n1\tac\tac\n1\tvirtutem\tvirtus\n1\tprovinciae\tprovincia\n1\tCaesar\tCaesar\n1\test\tesse\n1\tsatis\tsatis\n1\tgovernment\tgovernment\n1\tsocius\tsocius\n1\tprovincia\tprovincia\n1\tpublicus\tpublicus\n1\tcivis\tcivis\n1\tatque\tatque"
    subgraph_json: str = '{"exercise_id":"","exercise_type":"","frequency_analysis":null,"graph_data":{"directed":true,"graph":{},"links":[],"multigraph":true,"nodes":[{"annis_node_name":"urn:cts:latinLit:phi0448.phi001.perseus-lat2:1.1.1-1.1.1/doc1#sent1tok3","annis_node_type":"node","annis_tok":"Galli","annis_type":"node","id":"salt:/urn:cts:latinLit:phi0448.phi001.perseus-lat2:1.1.1-1.1.1/doc1#sent1tok3","is_oov":null,"udep_lemma":"Gallo","udep_upostag":"VERB","udep_xpostag":"L3|modQ|tem1|stAC","udep_feats":"Tense=Pres|VerbForm=Inf|Voice=Pass","solution":null}]},"solutions":[],"text_complexity":null,"uri":""}'
    test_args: List[str] = ["tests.py", "-test"]
    text_complexity_json_string: str = '{"all":54.53,"avg_w_len":5.79,"avg_w_per_sent":17.33,"lex_den":0.73,"n_abl_abs":0,"n_clause":1,"n_gerund":1,"n_inf":1,"n_part":1,"n_punct":3,"n_sent":3,"n_subclause":0,"n_types":48,"n_w":52,"pos":11}'
    text_list: List[Tuple[str, str]] = [("urn:cts:latinLit:phi0448.phi001.perseus-lat2:1.1.1", raw_text.split(".")[0]),
                                        ("urn:cts:latinLit:phi0448.phi001.perseus-lat2:1.1.2", raw_text.split(".")[1])]
    text_parts: List[TextPart] = [
        TextPart(citation=Citation(level=CitationLevel.book, label="2", value=2), text_value="text", sub_text_parts=[
            TextPart(
                citation=Citation(level=CitationLevel.chapter, label="23", value=23), text_value="inner text",
                sub_text_parts=[
                    TextPart(citation=Citation(level=CitationLevel.section, label="1", value=1),
                             text_value="subtext"),
                    TextPart(citation=Citation(level=CitationLevel.section, label="2", value=2))])])]
    udpipe_string: str = "# newpar\n# sent_id = 1\n# text = Caesar fortis est.\n1\tCaesar\tCaeso\tVERB\tC1|grn1|casA|gen1|stAN\tCase=Nom|Degree=Pos|Gender=Masc|Number=Sing\t2\tcsubj\t_\t_\n2\tfortis\tfortis\tADJ\tC1|grn1|casA|gen1|stAN\tCase=Nom|Degree=Pos|Gender=Masc|Number=Sing\t0\troot\t_\t_\n3\test\tsum\tAUX\tN3|modA|tem1|gen6|stAV\tMood=Ind|Number=Sing|Person=3|Tense=Pres|VerbForm=Fin|Voice=Act\t2\tcop\t_\tSpaceAfter=No\n4\t.\t.\tPUNCT\tPunc\t_\t2\tpunct\t_\t_\n\n# sent_id = 2\n# text = Galli moriuntur.\n1\tGalli\tGallus\tPRON\tF1|grn1|casJ|gen1|stPD\tCase=Nom|Degree=Pos|Gender=Masc|Number=Plur|PronType=Dem\t2\tnsubj:pass\t_\t_\n2\tmoriuntur\tmorior\tVERB\tL3|modJ|tem1|gen9|stAV\tMood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin|Voice=Pass\t0\troot\t_\tSpaceAfter=No\n3\t.\t.\tPUNCT\tPunc\t_\t2\tpunct\t_\tSpacesAfter=\\n\n\n"
    urn: str = "urn:cts:latinLit:phi0448.phi001.perseus-lat2:1.1.1-1.1.2"
    urn_custom: str = f"{CustomCorpusService.custom_corpora[4].corpus.source_urn}:2.23.1-2.23.1"
    xapi_json_string: str = '{"0":{"actor":{"account":{"name":"9a7eef78-b0b4-471d-b451-e47c9b20d231"},"objectType":"Agent"},"verb":{"id":"http://adlnet.gov/expapi/verbs/answered","display":{"en-US":"answered"}},"object":{"objectType":"Activity","definition":{"extensions":{"http://h5p.org/x-api/h5p-local-content-id":1},"interactionType":"fill-in","type":"http://adlnet.gov/expapi/activities/cmi.interaction","description":{"en-US":"<p>Matching: Assign the matching elements to each other!</p><br/>divisa __________<br/>dividit __________<br/>"},"correctResponsesPattern":["partes[,]Belgis"]}},"context":{"contextActivities":{"category":[{"id":"http://h5p.org/libraries/H5P.DragText-1.8","objectType":"Activity"}]}},"result":{"response":"Belgis[,]","score":{"min":0,"raw":0,"max":2,"scaled":0},"duration":"PT4.12S","completion":true}}}'

    @staticmethod
    def mock_add_eges(keys: List[str], w2v: Word2Vec, nearest_neighbor_count: int, min_count: int, graph: Graph):
        graph.add_edge("ueritas", "uera")
