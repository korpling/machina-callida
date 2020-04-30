"""Unit tests for testing the application functionality."""
# TODO: TEST BLINKER, GUNICORN, PSYCOPG2-BINARY AND COVERAGE IMPORTS
import copy
import logging
import ntpath
import os
from collections import OrderedDict
from threading import Thread
from unittest.mock import patch, MagicMock, mock_open
from zipfile import ZipFile

import rapidjson as json
import re
import shutil
import string
import sys
import time
import unittest
from multiprocessing import Process
from unittest import TestLoader
from datetime import datetime
from typing import Dict, List, Tuple, Type

from conllu import TokenList
from flask import Flask
from flask.testing import FlaskClient
from gensim.models import Word2Vec
from lxml import etree
from networkx import MultiDiGraph, Graph
from requests import HTTPError
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import session
from werkzeug.exceptions import NotFound
from werkzeug.wrappers import Response

import csm
import mcserver
from csm.app import create_csm_app
from mcserver.app import create_app, db, start_updater, full_init
from mcserver.app.api.exerciseAPI import map_exercise_data_to_database
from mcserver.app.api.vectorNetworkAPI import add_edges, get_concept_network
from mcserver.app.models import Corpus, UpdateInfo, ResourceType, Exercise, FileType, ExerciseType, ExerciseData, \
    NodeMC, LinkMC, GraphData, Phenomenon, CustomCorpus, AnnisResponse, Solution, DownloadableFile, Language, \
    VocabularyCorpus, SolutionElement, TextComplexityMeasure, FrequencyAnalysis, CitationLevel, FrequencyItem, \
    LearningResult, TextComplexity, Dependency, PartOfSpeech, Category, Choice, Actor, XapiStatement
from mcserver.app.services import AnnotationService, CorpusService, FileService, CustomCorpusService, DatabaseService, \
    XMLservice, TextService
from mcserver.config import TestingConfig, Config
from mocks import Mocks, MockResponse, MockW2V


class McTestCase(unittest.TestCase):
    """The test suite for the main application."""

    def mocked_requests_get(*args, **kwargs):
        if TestingConfig.SIMULATE_CORPUS_NOT_FOUND:
            return MockResponse(json.dumps(AnnisResponse().__dict__))
        elif TestingConfig.SIMULATE_HTTP_ERROR:
            raise HTTPError
        elif TestingConfig.SIMULATE_EMPTY_GRAPH:
            graph_data_raw: dict = dict(Mocks.annis_response_dict["graph_data_raw"])
            graph_data_raw["nodes"] = []
            return MockResponse(json.dumps(graph_data_raw))
        url: str = args[0]
        if url == Config.CTS_API_BASE_URL:
            if kwargs['params']['request'] == 'GetCapabilities':
                return MockResponse(Mocks.cts_capabilities_xml)
            return MockResponse(Mocks.cts_reff_xml)
        elif url.endswith(Config.SERVER_URI_CSM_SUBGRAPH):
            return MockResponse(json.dumps(Mocks.annis_response_dict))
        else:
            gd: GraphData = AnnotationService.map_graph_data(Mocks.annis_response_dict["graph_data_raw"])
            return MockResponse(json.dumps(gd.serialize()))

    def mocked_requests_post(*args, **kwargs):
        url: str = args[0]
        if url.endswith(Config.SERVER_URI_TEXT_COMPLEXITY):
            return MockResponse(Mocks.text_complexity_json_string)
        else:
            ed1: ExerciseData = AnnotationService.map_graph_data_to_exercise(
                Mocks.annis_response_dict["graph_data_raw"],
                "", [Solution(target=SolutionElement(
                    salt_id='salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159692tok1'))])
            ed2: ExerciseData = AnnotationService.map_graph_data_to_exercise(
                Mocks.annis_response_dict["graph_data_raw"],
                "", [Solution(target=SolutionElement(
                    salt_id='salt:/urn:custom:latinLit:proiel.pal-agr.lat:1.1.1/doc1#sent159695tok10'))])
            ed2.graph.nodes = ed2.graph.nodes[42:]
            return MockResponse(json.dumps([ed1.serialize(), ed2.serialize()]))

    def setUp(self):
        """Initializes the testing environment."""
        self.start_time = time.time()
        if os.path.exists(Config.GRAPH_DATABASE_DIR):
            shutil.rmtree(Config.GRAPH_DATABASE_DIR)
        patcher = patch.object(TextService, "init_stop_words_latin")
        self.addCleanup(patcher.stop)
        patcher.start()
        self.app: Flask = create_app(TestingConfig)
        self.app.logger.setLevel(logging.CRITICAL)
        self.assertIsInstance(self.app, Flask)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.app.testing = True
        self.client: FlaskClient = self.app.test_client()
        self.assertIsInstance(self.client, FlaskClient)
        UpdateInfo.query.delete()
        Corpus.query.delete()

    def tearDown(self):
        """Finishes testing by removing the traces."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        print("{0}: {1} seconds".format(self.id(), "%.2f" % (time.time() - self.start_time)))

    @staticmethod
    def add_corpus(corpus: Corpus):
        """ Adds a corpus to the database. """
        db.session.add(corpus)
        UpdateInfo.query.delete()
        ui_cts: UpdateInfo = UpdateInfo(resource_type=ResourceType.cts_data, last_modified_time=datetime.utcnow())
        db.session.add(ui_cts)
        db.session.commit()

    @staticmethod
    def clear_folder(folder_path: str):
        """ Deletes every file in a folder. """
        for f in [x for x in os.listdir(folder_path) if x != ".gitignore"]:
            os.remove(os.path.join(folder_path, f))

    def test_api_corpus_delete(self):
        """ Deletes a single corpus. """
        response: Response = self.client.delete(Mocks.corpora[0].uri)
        self.assertEqual(response.status_code, 404)
        McTestCase.add_corpus(Mocks.corpora[0])
        response = self.client.delete(Mocks.corpora[0].uri)
        data_json: dict = json.loads(response.get_data())
        self.assertEqual(data_json, {"result": True})
        Corpus.query.delete()
        UpdateInfo.query.delete()
        # dirty hack so we can reuse it in other tests
        session.make_transient(Mocks.corpora[0])

    def test_api_corpus_get(self):
        """ Gets information about a single corpus. """
        response: Response = self.client.get(Mocks.corpora[0].uri)
        self.assertEqual(response.status_code, 404)
        McTestCase.add_corpus(Mocks.corpora[0])
        response: Response = self.client.get(Mocks.corpora[0].uri)
        data_json: dict = json.loads(response.get_data())
        actual_corpus: Corpus = Corpus(json_dict=data_json["corpus"])
        self.assertEqual(actual_corpus, Mocks.corpora[0])
        Corpus.query.delete()
        UpdateInfo.query.delete()
        # dirty hack so we can reuse it in other tests
        session.make_transient(Mocks.corpora[0])

    def test_api_corpus_list_get(self):
        """Adds multiple texts to the database and queries them all."""

        class MockFilterBy:
            def __init__(self, do_raise: bool = False, ui: UpdateInfo = None):
                self.do_raise: bool = do_raise
                self.ui: UpdateInfo = ui

            def first(self):
                if self.do_raise:
                    raise OperationalError("error", [], "")
                else:
                    return self.ui

        def expect_result(self: McTestCase, mock: MagicMock, do_raise: bool, lut: str, result: object,
                          lmt: datetime = datetime.utcnow()):
            ui: UpdateInfo = UpdateInfo(resource_type=ResourceType.cts_data, last_modified_time=lmt)
            mfb: MockFilterBy = MockFilterBy(do_raise, ui)
            mock.query.filter_by.return_value = mfb
            response: Response = self.client.get(TestingConfig.SERVER_URI_CORPORA,
                                                 query_string=dict(last_update_time=lut))
            data_json = json.loads(response.get_data())
            if data_json:
                data_json = [Corpus(json_dict=x) for x in data_json["corpora"]]
            self.assertEqual(data_json, result)

        with patch.object(mcserver.app.api.corpusListAPI, "UpdateInfo") as mock_update_info:
            expect_result(self, mock_update_info, True, "0", None)
            expect_result(self, mock_update_info, False, str(int(datetime.utcnow().timestamp() * 1000)), None,
                          datetime.fromtimestamp(0))
            db.session.add_all(Mocks.corpora)
            db.session.commit()
            expect_result(self, mock_update_info, False, "0", Mocks.corpora, datetime.fromtimestamp(time.time()))
        Corpus.query.delete()
        UpdateInfo.query.delete()
        # dirty hack so we can reuse it in other tests
        session.make_transient(Mocks.corpora[0])

    def test_api_corpus_put(self):
        """ Changes information about a single corpus. """
        response: Response = self.client.put(Mocks.corpora[0].uri)
        self.assertEqual(response.status_code, 404)
        McTestCase.add_corpus(Mocks.corpora[0])
        old_title: str = Mocks.corpora[0].title
        new_title: str = "new_title"
        response: Response = self.client.put(Mocks.corpora[0].uri, data=dict(title=new_title))
        data_json: dict = json.loads(response.get_data())
        new_corpus: Corpus = Corpus(json_dict=data_json["corpus"])
        self.assertEqual(new_corpus.title, Mocks.corpora[0].title)
        Mocks.corpora[0].title = old_title
        Corpus.query.delete()
        UpdateInfo.query.delete()
        # dirty hack so we can reuse it in other tests
        session.make_transient(Mocks.corpora[0])

    def test_api_exercise_get(self):
        """ Retrieves an existing exercise by its exercise ID. """
        response: Response = self.client.get(Config.SERVER_URI_EXERCISE, query_string=dict(eid=""))
        self.assertEqual(response.status_code, 404)
        old_urn: str = Mocks.exercise.urn
        Mocks.exercise.urn = ""
        db.session.add(Mocks.exercise)
        db.session.commit()
        with patch.object(CorpusService, "get_corpus", side_effect=[AnnisResponse(), Mocks.annis_response]):
            response = self.client.get(Config.SERVER_URI_EXERCISE, query_string=dict(eid=Mocks.exercise.eid))
            self.assertEqual(response.status_code, 404)
            Mocks.exercise.urn = old_urn
            db.session.commit()
            response = self.client.get(Config.SERVER_URI_EXERCISE, query_string=dict(eid=Mocks.exercise.eid))
            graph_dict: dict = json.loads(response.data.decode("utf-8"))
            ar: AnnisResponse = AnnisResponse(json_dict=graph_dict)
            self.assertEqual(len(ar.nodes), 52)
            Exercise.query.delete()
            session.make_transient(Mocks.exercise)
            self.app_context.push()

    def test_api_exercise_list_get(self):
        """ Retrieves a list of available exercises. """
        ui_exercises: UpdateInfo = UpdateInfo(resource_type=ResourceType.exercise_list,
                                              last_modified_time=datetime.fromtimestamp(1))
        db.session.add(ui_exercises)
        db.session.commit()
        args: dict = dict(lang="fr", last_update_time=int(time.time()))
        response: Response = self.client.get(TestingConfig.SERVER_URI_EXERCISE_LIST, query_string=args)
        self.assertEqual(json.loads(response.get_data()), [])
        args["last_update_time"] = 0
        db.session.add(Mocks.exercise)
        db.session.commit()
        response = self.client.get(TestingConfig.SERVER_URI_EXERCISE_LIST, query_string=args)
        exercises: List[Exercise] = [Exercise(json_dict=x) for x in json.loads(response.get_data())]  # .decode("utf-8")
        self.assertEqual(len(exercises), 1)
        args = dict(lang=Language.English.value, vocabulary=VocabularyCorpus.agldt.name, frequency_upper_bound=500)
        response = self.client.get(TestingConfig.SERVER_URI_EXERCISE_LIST, query_string=args)
        exercises: List[dict] = json.loads(response.get_data())  # .decode("utf-8")
        self.assertTrue(exercises[0]["matching_degree"])
        Exercise.query.delete()
        session.make_transient(Mocks.exercise)

    def test_api_file_get(self):
        """Gets an existing exercise"""
        ui_file: UpdateInfo = UpdateInfo(resource_type=ResourceType.file_api_clean,
                                         last_modified_time=datetime.fromtimestamp(1))
        db.session.add(ui_file)
        db.session.commit()
        # create a fake old file, to be deleted on the next GET request
        FileService.create_tmp_file(FileType.xml, "old")
        args: dict = dict(type=FileType.xml.value, id=Mocks.exercise.eid, solution_indices="[0]")
        response: Response = self.client.get(TestingConfig.SERVER_URI_FILE, query_string=args)
        self.assertEqual(response.status_code, 404)
        file_path: str = os.path.join(Config.TMP_DIRECTORY, Mocks.exercise.eid + "." + FileType.xml.value)
        file_content: str = "<xml></xml>"
        with open(file_path, "w+") as f:
            f.write(file_content)
        ui_file.last_modified_time = datetime.utcnow()
        db.session.commit()
        del ui_file
        response = self.client.get(TestingConfig.SERVER_URI_FILE, query_string=args)
        os.remove(file_path)
        self.assertEqual(response.data.decode("utf-8"), file_content)
        # add the mapped exercise to the database
        db.session.add(Mocks.exercise)
        db.session.commit()
        args["type"] = FileType.pdf.value
        response = self.client.get(TestingConfig.SERVER_URI_FILE, query_string=args)
        # the PDFs are not deterministically reproducible because the creation date etc. is written into them
        self.assertTrue(response.data.startswith(Mocks.exercise_pdf))
        Exercise.query.delete()
        session.make_transient(Mocks.exercise)

    def test_api_file_post(self):
        """ Posts exercise data to be saved temporarily or permanently on the server, e.g. for downloading. """
        learning_result: str = Mocks.xapi_json_string
        data_dict: dict = dict(learning_result=learning_result)
        self.client.post(TestingConfig.SERVER_URI_FILE, headers=Mocks.headers_form_data, data=data_dict)
        lrs: List[LearningResult] = LearningResult.query.all()
        self.assertEqual(len(lrs), 1)
        data_dict: dict = dict(file_type=FileType.xml.name, urn=Mocks.urn_custom, html_content="<html></html>")
        response: Response = self.client.post(TestingConfig.SERVER_URI_FILE, headers=Mocks.headers_form_data,
                                              data=data_dict)
        file_name = json.loads(response.data.decode("utf-8"))
        self.assertTrue(file_name.endswith(".xml"))
        os.remove(os.path.join(Config.TMP_DIRECTORY, file_name))
        LearningResult.query.delete()

    def test_api_frequency_get(self):
        """ Requests a frequency analysis for a given URN. """
        with patch.object(mcserver.app.services.corpusService.requests, "get", return_value=MockResponse(
                json.dumps([FrequencyItem(values=[], phenomena=[], count=[]).serialize()]))):
            response: Response = self.client.get(TestingConfig.SERVER_URI_FREQUENCY,
                                                 query_string=dict(urn=Mocks.urn_custom))
            result_list: List[dict] = json.loads(response.data.decode("utf-8"))
            fa: FrequencyAnalysis = FrequencyAnalysis(json_list=result_list)
            self.assertEqual(len(fa), 1)

    def test_api_h5p_get(self):
        """ Requests a H5P JSON file for a given exercise. """
        args: dict = dict(eid=Mocks.exercise.eid, lang=Language.English.value, solution_indices="[0]")
        response: Response = self.client.get(TestingConfig.SERVER_URI_H5P, query_string=args)
        self.assertEqual(response.status_code, 404)
        db.session.add(Mocks.exercise)
        db.session.commit()
        response = self.client.get(TestingConfig.SERVER_URI_H5P, query_string=args)
        self.assertIn(Mocks.h5p_json_cloze[1:-1], response.data.decode("utf-8"))
        Mocks.exercise.exercise_type = ExerciseType.kwic.value
        db.session.commit()
        response = self.client.get(TestingConfig.SERVER_URI_H5P, query_string=args)
        self.assertEqual(response.status_code, 422)
        Mocks.exercise.exercise_type = ExerciseType.matching.value
        db.session.commit()
        response = self.client.get(TestingConfig.SERVER_URI_H5P, query_string=args)
        self.assertIn(Mocks.h5p_json_matching[1:-1], response.data.decode("utf-8"))
        Mocks.exercise.exercise_type = ExerciseType.cloze.value
        args["lang"] = "fr"
        response = self.client.get(TestingConfig.SERVER_URI_H5P, query_string=args)
        self.assertIn(Mocks.h5p_json_cloze[1:-1], response.data.decode("utf-8"))
        Exercise.query.delete()
        session.make_transient(Mocks.exercise)

    @patch('mcserver.app.api.kwicAPI.requests.post', side_effect=mocked_requests_post)
    def test_api_kwic_post(self, mock_post: MagicMock):
        """ Posts an AQL query to create a KWIC visualization in SVG format. """
        data_dict: dict = dict(search_values=Mocks.exercise.search_values, urn=Mocks.urn_custom)
        response: Response = self.client.post(TestingConfig.SERVER_URI_KWIC, headers=Mocks.headers_form_data,
                                              data=data_dict)
        self.assertTrue(response.data.startswith(Mocks.kwic_svg))

    def test_api_not_found(self):
        """Checks the 404 response in case of an invalid API query URL."""
        with self.assertRaises(NotFound):
            self.client.get("/")

    @patch('mcserver.app.services.textComplexityService.requests.post', side_effect=mocked_requests_post)
    @patch('mcserver.app.services.corpusService.requests.get', side_effect=mocked_requests_get)
    def test_api_raw_text_get(self, mock_post_tcs: MagicMock, mock_get_cs: MagicMock):
        """ Retrieves the raw text for a given URN. """
        TestingConfig.SIMULATE_CORPUS_NOT_FOUND = True
        response: Response = self.client.get(TestingConfig.SERVER_URI_RAW_TEXT, query_string=dict(urn=Mocks.urn_custom))
        self.assertEqual(response.status_code, 404)
        TestingConfig.SIMULATE_CORPUS_NOT_FOUND = False
        response = self.client.get(TestingConfig.SERVER_URI_RAW_TEXT, query_string=dict(urn=Mocks.urn_custom))
        self.assertEqual(len(json.loads(response.data.decode("utf-8"))["nodes"]), 52)
        TestingConfig.SIMULATE_EMPTY_GRAPH = True
        response = self.client.get(TestingConfig.SERVER_URI_RAW_TEXT, query_string=dict(urn=Mocks.urn_custom))
        self.assertEqual(response.status_code, 404)
        TestingConfig.SIMULATE_EMPTY_GRAPH = False

    @patch('mcserver.app.api.staticExercisesAPI.requests.get', side_effect=mocked_requests_get)
    def test_api_static_exercises_get(self, mock_get: MagicMock):
        """ Retrieves static exercises from the frontend and publishes deep URLs for each one of them. """
        exercises: List[Tuple[str, str, str]] = [
            (Config.H5P_FILL_BLANKS,) + Mocks.h5p_json_fill_blanks_1,
            (Config.H5P_FILL_BLANKS,) + Mocks.h5p_json_fill_blanks_3,
            (Config.H5P_FILL_BLANKS,) + Mocks.h5p_json_fill_blanks_4,
            (Config.H5P_FILL_BLANKS,) + Mocks.h5p_json_fill_blanks_13,
            (Config.H5P_DRAG_TEXT, "1_en", Mocks.h5p_json_cloze),
            (Config.H5P_MULTI_CHOICE, "1_en", Mocks.h5p_json_multi_choice),
            (Config.H5P_MULTI_CHOICE, "2_en", Mocks.h5p_json_multi_choice_2),
            (Config.H5P_MULTI_CHOICE,) + Mocks.h5p_json_multi_choice_9,
            (Config.H5P_VOC_LIST, "1_en", Mocks.h5p_json_voc_list)]
        paths: List[str] = []
        for exercise in exercises:
            file_name: str = exercise[1] + ".json"
            file_path: str = os.path.join(Config.TMP_DIRECTORY, exercise[0], "content", file_name)
            os.makedirs(os.path.split(file_path)[0], exist_ok=True)
            json.dump(json.loads(exercise[2]), open(file_path, "w+"))
            paths.append(file_path)
        with ZipFile(TestingConfig.STATIC_EXERCISES_ZIP_FILE_PATH, "w") as z:
            for path in paths:
                z.write(path)
        for exercise in exercises:
            shutil.rmtree(os.path.join(Config.TMP_DIRECTORY, exercise[0]), ignore_errors=True)
        zip_content: bytes = open(TestingConfig.STATIC_EXERCISES_ZIP_FILE_PATH, "rb").read()
        with patch.object(mcserver.app.api.staticExercisesAPI.requests, "get",
                          side_effect=[MockResponse("{}", ok=False), MockResponse("{}", content=zip_content)]):
            with patch.object(AnnotationService, "get_udpipe", return_value=Mocks.static_exercises_udpipe_string):
                response = self.client.get(TestingConfig.SERVER_URI_STATIC_EXERCISES)
                self.assertEqual(response.status_code, 503)
                response: Response = self.client.get(TestingConfig.SERVER_URI_STATIC_EXERCISES)
                os.remove(TestingConfig.STATIC_EXERCISES_ZIP_FILE_PATH)
                self.assertGreater(len(response.data.decode("utf-8")), 1900)

    @patch('mcserver.app.services.corpusService.requests.get', side_effect=mocked_requests_get)
    def test_api_subgraph_get(self, mock_get: MagicMock):
        """ Retrieves subgraph data for a given URN. """
        ar: AnnisResponse = CorpusService.get_subgraph(Mocks.urn_custom, 'tok="quarum"', 0, 0, False)
        self.assertEqual(len(ar.solutions), 3)

    @patch('mcserver.app.services.corpusService.requests.get', side_effect=mocked_requests_get)
    @patch('mcserver.app.services.textComplexityService.requests.post', side_effect=mocked_requests_post)
    def test_api_text_complexity_get(self, mock_get: MagicMock, mock_post: MagicMock):
        """ Calculates text complexity measures for a given URN. """
        args: dict = dict(urn=Mocks.urn_custom, measure=TextComplexityMeasure.all.name)
        response: Response = self.client.get(TestingConfig.SERVER_URI_TEXT_COMPLEXITY, query_string=args)
        self.assertEqual(response.data.decode("utf-8"), Mocks.text_complexity_json_string)
        args["measure"] = "n_w"
        response = self.client.get(TestingConfig.SERVER_URI_TEXT_COMPLEXITY, query_string=args)
        self.assertEqual(json.loads(response.data.decode("utf-8"))["n_w"], 52)

    @patch('MyCapytain.retrievers.cts5.requests.get', side_effect=mocked_requests_get)
    def test_api_valid_reff_get(self, mock_get: MagicMock):  #
        """ Retrieves possible citations for a given URN. """
        args: dict = dict(urn=Mocks.urn_custom[:-14])
        response: Response = self.client.get(TestingConfig.SERVER_URI_VALID_REFF, query_string=args)
        self.assertEqual(len(json.loads(response.data.decode("utf-8"))), 3)
        McTestCase.clear_folder(Config.REFF_CACHE_DIRECTORY)
        args["urn"] = f"{Mocks.urn_custom[:-13]}4"
        response = self.client.get(TestingConfig.SERVER_URI_VALID_REFF, query_string=args)
        self.assertEqual(response.status_code, 404)
        McTestCase.clear_folder(Config.REFF_CACHE_DIRECTORY)
        args["urn"] = f"{Mocks.urn_custom[:-13]}abc"
        response = self.client.get(TestingConfig.SERVER_URI_VALID_REFF, query_string=args)
        self.assertEqual(response.status_code, 400)
        McTestCase.clear_folder(Config.REFF_CACHE_DIRECTORY)
        TestingConfig.SIMULATE_HTTP_ERROR = True
        self.assertEqual(len(CorpusService.get_standard_corpus_reff(Mocks.urn[:-8])), 0)
        TestingConfig.SIMULATE_HTTP_ERROR = False
        reff: List[str] = CorpusService.get_standard_corpus_reff(Mocks.urn[:-8])
        self.assertEqual(len(reff), 7)

    def test_api_vector_network_get(self):
        """ Builds a network of semantically similar vectors for a given list of words. """
        with patch.object(mcserver.app.api.vectorNetworkAPI, "add_edges", side_effect=Mocks.mock_add_eges):
            with patch.object(mcserver.app.api.vectorNetworkAPI.Word2Vec, "load", return_value=MockW2V()):
                args: dict = dict(search_regex='ueritas', nearest_neighbor_count=150, min_count=6)
                response: Response = self.client.get(TestingConfig.SERVER_URI_VECTOR_NETWORK, query_string=args)
                svg_string: str = json.loads(response.data.decode("utf-8"))
                self.assertGreater(len(svg_string), 6500)

    def test_api_vector_network_post(self):
        """ Returns contexts that are semantically similar to a given query. """
        mock_data: str = "This is a sentence.\nAnd here is yet another one.\n"
        with patch("mcserver.app.api.vectorNetworkAPI.open", mock_open(read_data=mock_data)):
            with patch.object(mcserver.app.api.vectorNetworkAPI.Word2Vec, "load", return_value=MockW2V()):
                data_dict: dict = dict(search_regex='uera', nearest_neighbor_count=10)
                response: Response = self.client.post(TestingConfig.SERVER_URI_VECTOR_NETWORK,
                                                      headers=Mocks.headers_form_data, data=data_dict)
                self.assertEqual(len(json.loads(response.data.decode("utf-8"))), 2)

    @patch('mcserver.app.services.corpusService.requests.get', side_effect=mocked_requests_get)
    @patch('mcserver.app.services.textComplexityService.requests.post', side_effect=mocked_requests_post)
    def test_api_vocabulary_get(self, mock_get: MagicMock, mock_post: MagicMock):
        """ Calculates lexical overlap between a text (specified by URN) and a static vocabulary. """
        args: dict = dict(query_urn=Mocks.urn_custom, show_oov=True, vocabulary=VocabularyCorpus.agldt.name,
                          frequency_upper_bound=500)
        response: Response = self.client.get(TestingConfig.SERVER_URI_VOCABULARY, query_string=args)
        ar: AnnisResponse = AnnisResponse(json_dict=json.loads(response.data.decode("utf-8")))
        self.assertTrue(NodeMC(json_dict=ar.nodes[3]).is_oov)
        args["show_oov"] = False
        args["frequency_upper_bound"] = 6000
        response = self.client.get(TestingConfig.SERVER_URI_VOCABULARY, query_string=args)
        self.assertEqual(json.loads(response.data.decode("utf-8"))[0]["matching_degree"], 90.9090909090909)

    def test_app_init(self):
        """Creates a CSM app in testing mode."""
        CorpusService.init_graphannis_logging()
        log_path: str = os.path.join(os.getcwd(), Config.GRAPHANNIS_LOG_PATH)
        self.assertTrue(os.path.exists(log_path))
        os.remove(log_path)
        with patch.object(sys, 'argv', Mocks.test_args):
            app: Flask = csm.get_app()
            self.assertIsInstance(app, Flask)
            self.assertTrue(app.config["TESTING"])
            UpdateInfo.query.delete()
            app = mcserver.get_app()
            self.assertIsInstance(app, Flask)
            self.assertTrue(app.config["TESTING"])
        self.app_context.push()
        Corpus.query.delete()

    def test_create_app(self):
        """Creates a new Flask application and configures it. Initializes the application and the database."""
        with patch.object(sys, "argv", [None, None, Config.FLASK_MIGRATE]):
            with patch.object(mcserver.app, "init_app_common", return_value=Flask(__name__)):
                cfg: Type[Config] = TestingConfig
                old_uri: str = cfg.SQLALCHEMY_DATABASE_URI
                create_app(cfg)
                self.assertEqual(cfg.SQLALCHEMY_DATABASE_URI, Config.DATABASE_URL_LOCAL)
                cfg.SQLALCHEMY_DATABASE_URI = old_uri
        self.app_context.push()

    def test_init_corpus_storage_manager(self):
        """ Initializes the corpus storage manager. """
        ui_cts: UpdateInfo = UpdateInfo(resource_type=ResourceType.cts_data, last_modified_time=datetime.utcnow())
        db.session.add(ui_cts)
        db.session.commit()
        csm_process: Process
        with patch.object(sys, 'argv', Mocks.test_args):
            os.environ[Config.COVERAGE_ENVIRONMENT_VARIABLE] = Config.COVERAGE_CONFIGURATION_FILE_NAME
            csm_process = Process(target=csm.run_app)
        csm_process.start()
        self.app_context.push()
        self.assertTrue(csm_process.is_alive())
        csm_process.terminate()
        csm_process.join()
        self.assertFalse(csm_process.is_alive())
        UpdateInfo.query.delete()

    @patch('mcserver.app.services.textComplexityService.requests.post', side_effect=mocked_requests_post)
    def test_map_exercise_data_to_database(self, mock_post: MagicMock):
        """Maps exercise data to the database and saves it for later access."""
        ui_exercises: UpdateInfo = UpdateInfo(resource_type=ResourceType.exercise_list,
                                              last_modified_time=datetime.fromtimestamp(1))
        db.session.add(ui_exercises)
        db.session.commit()
        exercise_expected: Exercise = Mocks.exercise
        exercise: Exercise = map_exercise_data_to_database(
            solutions=[Solution(json_dict=x) for x in json.loads(exercise_expected.solutions)],
            exercise_data=Mocks.exercise_data, instructions=exercise_expected.instructions,
            exercise_type=exercise_expected.exercise_type,
            exercise_type_translation=exercise_expected.exercise_type_translation, xml_guid=exercise_expected.eid,
            conll=exercise_expected.conll, correct_feedback=exercise_expected.correct_feedback,
            partially_correct_feedback=exercise_expected.partially_correct_feedback, urn=Mocks.urn_custom,
            incorrect_feedback=exercise_expected.incorrect_feedback, search_values=exercise_expected.search_values,
            general_feedback=exercise_expected.general_feedback, work_author="", work_title="")
        expected_values: List[str] = [
            exercise_expected.conll, exercise_expected.general_feedback, exercise_expected.incorrect_feedback,
            exercise_expected.search_values, exercise_expected.partially_correct_feedback,
            exercise_expected.correct_feedback, exercise_expected.instructions,
            exercise_expected.exercise_type_translation, exercise_expected.exercise_type, exercise_expected.solutions,
            exercise_expected.uri, exercise_expected.eid]
        actual_values: List[str] = [
            exercise.conll, exercise.general_feedback, exercise.incorrect_feedback, exercise.search_values,
            exercise.partially_correct_feedback, exercise.correct_feedback, exercise.instructions,
            exercise.exercise_type_translation, exercise.exercise_type, exercise.solutions, exercise.uri, exercise.eid]
        self.assertEqual(expected_values, actual_values)
        exercise_from_db: Exercise = Exercise.query.one()
        self.assertEqual(exercise, exercise_from_db)
        Exercise.query.delete()
        session.make_transient(Mocks.exercise)

    @patch('MyCapytain.retrievers.cts5.requests.get', side_effect=mocked_requests_get)
    def test_update_corpora(self, mock_get: MagicMock):
        """Checks the remote repositories for new corpora to be included in our database."""
        CorpusService.update_corpora()
        self.assertEqual(len(CorpusService.existing_corpora), 1)
        ec: Corpus = CorpusService.existing_corpora[0]
        ec.title = ""
        db.session.commit()
        McTestCase.add_corpus(Corpus(source_urn="123"))
        cls: List[CitationLevel] = [ec.citation_level_1, ec.citation_level_2, ec.citation_level_3]
        CorpusService.update_corpus(ec.title, ec.source_urn, ec.author, cls, ec)
        self.assertFalse(ec.title)
        CorpusService.update_corpora()
        self.assertTrue(ec.title)
        Corpus.query.delete()


class CsmTestCase(unittest.TestCase):
    """The test suite for the Corpus Storage Manager application."""

    @staticmethod
    def set_up_mcserver() -> FlaskClient:
        app: Flask = create_app(TestingConfig)
        app.logger.setLevel(logging.CRITICAL)
        app.testing = True
        return app.test_client()

    def mocked_requests_post(*args, **kwargs):
        url: str = args[0]
        if url.endswith(Config.SERVER_URI_TEXT_COMPLEXITY):
            return MockResponse(Mocks.text_complexity_json_string)
        elif url[-1] == '/':
            return MockResponse("}{")
        else:
            return MockResponse(json.dumps(Mocks.annis_response_dict))

    def setUp(self):
        """Initializes the testing environment."""
        self.start_time = time.time()
        if os.path.exists(Config.GRAPH_DATABASE_DIR):
            shutil.rmtree(Config.GRAPH_DATABASE_DIR)
        patcher = patch.object(TextService, "init_stop_words_latin")
        self.addCleanup(patcher.stop)
        patcher.start()
        self.app: Flask = create_csm_app(TestingConfig)
        self.app.logger.setLevel(logging.CRITICAL)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.app.testing = True
        self.client: FlaskClient = self.app.test_client()
        UpdateInfo.query.delete()
        Corpus.query.delete()

    def tearDown(self):
        """Finishes testing by removing the traces."""
        Config.CORPUS_STORAGE_MANAGER.__exit__(None, None, None)
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        print("{0}: {1} seconds".format(self.id(), "%.2f" % (time.time() - self.start_time)))

    def test_api_annis_find(self):
        """Retrieves search results from ANNIS for a given corpus and AQL query."""
        disk_urn: str = AnnotationService.get_disk_urn(Mocks.urn_custom)
        AnnotationService.map_conll_to_graph(corpus_name=Mocks.urn_custom, conll=Mocks.annotations,
                                             cs=Config.CORPUS_STORAGE_MANAGER, file_name=disk_urn)
        response: Response = self.client.get(Config.SERVER_URI_ANNIS_FIND,
                                             query_string=dict(urn=Mocks.urn_custom, aql="tok"))
        matches: List[str] = json.loads(response.get_data())
        self.assertEqual(len(matches), 6)
        solutions: List[Solution] = CorpusService.get_matches(Mocks.urn_custom, ['tok ->dep tok'],
                                                              [Phenomenon.dependency])
        self.assertEqual(len(solutions), 5)
        solutions = CorpusService.get_matches(Mocks.urn_custom, ['upostag="VERB" ->dep tok'],
                                              [Phenomenon.partOfSpeech, Phenomenon.dependency])
        self.assertEqual(len(solutions), 5)
        solutions = CorpusService.get_matches(Mocks.urn_custom, ['tok ->dep tok ->dep tok'],
                                              [Phenomenon.dependency, Phenomenon.partOfSpeech])
        self.assertEqual(len(solutions), 3)

    def test_api_csm_get(self):
        """Gets the raw text for a specific URN."""
        ret_vals: List[AnnisResponse] = [AnnisResponse(), Mocks.annis_response]
        with patch.object(CorpusService, "get_corpus", side_effect=ret_vals):
            response: Response = self.client.get(TestingConfig.SERVER_URI_CSM, query_string=dict(urn=Mocks.urn[:5]))
            self.assertEqual(response.status_code, 404)
            response: Response = self.client.get(TestingConfig.SERVER_URI_CSM, query_string=dict(urn=Mocks.urn_custom))
            graph_data_raw: dict = json.loads(response.get_data().decode("utf-8"))
            graph_data: GraphData = GraphData(json_dict=graph_data_raw)
            text_raw = " ".join(x.annis_tok for x in graph_data.nodes)
            # remove the spaces before punctuation because, otherwise, the parser won't work correctly
            received_text: str = re.sub('[ ]([{0}])'.format(string.punctuation), r'\1', text_raw)
            expected_text: str = "Pars est prima prudentiae ipsam cui praecepturus es aestimare personam."
            self.assertIn(expected_text, received_text)

    @patch('mcserver.app.services.corpusService.requests.post', side_effect=mocked_requests_post)
    @patch('mcserver.app.services.textComplexityService.requests.post', side_effect=mocked_requests_post)
    def test_api_exercise_post(self, mock_post_cs: MagicMock, mock_post_tcs: MagicMock):
        """ Creates a new exercise from scratch. """
        ui_exercises: UpdateInfo = UpdateInfo(resource_type=ResourceType.exercise_list,
                                              last_modified_time=datetime.fromtimestamp(1))
        db.session.add(ui_exercises)
        db.session.commit()
        client: FlaskClient = CsmTestCase.set_up_mcserver()
        data_dict: dict = dict(urn=Mocks.exercise.urn, type=ExerciseType.matching.value,
                               search_values=Mocks.exercise.search_values)
        response: Response = client.post(Config.SERVER_URI_EXERCISE, headers=Mocks.headers_form_data, data=data_dict)
        ar: AnnisResponse = AnnisResponse(json_dict=json.loads(response.data.decode("utf-8")))
        self.assertEqual(len(ar.solutions), 3)
        Config.CORPUS_STORAGE_MANAGER_PORT = f"{Config.CORPUS_STORAGE_MANAGER_PORT}/"
        response: Response = client.post(Config.SERVER_URI_EXERCISE, headers=Mocks.headers_form_data, data=data_dict)
        self.assertEqual(response.status_code, 500)
        Config.CORPUS_STORAGE_MANAGER_PORT = int(Config.CORPUS_STORAGE_MANAGER_PORT[:-1])
        self.app_context.push()

    def test_api_frequency_get(self):
        """ Requests a frequency analysis for a given URN. """
        expected_fa: FrequencyAnalysis = FrequencyAnalysis()
        expected_fa.append(
            FrequencyItem(values=[Dependency.object.name], phenomena=[Phenomenon.dependency], count=1))
        expected_fa.append(
            FrequencyItem(values=[PartOfSpeech.adjective.name], phenomena=[Phenomenon.partOfSpeech], count=1))
        with patch.object(CorpusService, "get_frequency_analysis", return_value=expected_fa):
            response: Response = self.client.get(TestingConfig.SERVER_URI_FREQUENCY,
                                                 query_string=dict(urn=Mocks.urn_custom))
            result_list: List[dict] = json.loads(response.data.decode("utf-8"))
            fa: FrequencyAnalysis = FrequencyAnalysis(json_list=result_list)
            self.assertEqual(fa[0].values, expected_fa[0].values)
            self.assertEqual(fa[1].values[0], None)

    def test_api_subgraph_get(self):
        """ Retrieves subgraph data for a given URN. """
        args: dict = dict(urn=Mocks.urn_custom, aqls=['tok="quarum"'], ctx_left="0", ctx_right="0")
        response: Response = self.client.get(TestingConfig.SERVER_URI_CSM_SUBGRAPH, query_string=args)
        self.assertEqual(response.data.decode("utf-8"), Mocks.subgraph_json)

    def test_api_subgraph_post(self):
        """ Retrieves KWIC-style subgraph data for a given URN. """
        args: dict = dict(urn=Mocks.urn_custom, aqls=['tok="quarum"'], ctx_left="5", ctx_right="5")
        response: Response = self.client.post(TestingConfig.SERVER_URI_CSM_SUBGRAPH, data=json.dumps(args))
        results_list: list = json.loads(response.data.decode("utf-8"))
        exercise_data_list: List[ExerciseData] = [ExerciseData(json_dict=x) for x in results_list]
        self.assertEqual(len(exercise_data_list[0].graph.nodes), 10)
        with self.assertRaises(NotImplementedError):
            AnnotationService.get_single_subgraph("", [])

    def test_api_text_complexity_get(self):
        """ Calculates text complexity measures for a given URN. """
        args: dict = dict(urn=Mocks.urn_custom, measure=TextComplexityMeasure.all.name)
        response: Response = self.client.post(TestingConfig.SERVER_URI_TEXT_COMPLEXITY, data=json.dumps(args))
        tc: TextComplexity = TextComplexity(json_dict=json.loads(response.data.decode("utf-8")))
        self.assertEqual(tc.pos, 8)
        args["measure"] = "n_w"
        response = self.client.post(TestingConfig.SERVER_URI_TEXT_COMPLEXITY, data=json.dumps(args))
        tc = TextComplexity(json_dict=json.loads(response.data.decode("utf-8")))
        self.assertEqual(tc.n_w, 14)

    @patch('mcserver.app.services.corpusService.CorpusService.update_corpora')
    def test_check_corpus_list_age(self, mock_update: MagicMock):
        """Checks whether the list of available corpora needs to be updated."""
        ui_cts: UpdateInfo = UpdateInfo(resource_type=ResourceType.cts_data,
                                        last_modified_time=datetime.fromtimestamp(1))
        db.session.add(ui_cts)
        db.session.commit()
        utc_now: datetime = datetime.utcnow()
        DatabaseService.check_corpus_list_age(self.app)
        ui_cts: UpdateInfo = UpdateInfo.query.filter_by(resource_type=ResourceType.cts_data.name).first()
        self.assertGreater(ui_cts.last_modified_time, utc_now)
        UpdateInfo.query.delete()

    def test_corpus_storage_manager(self):
        """Performs an end-to-end test for the Corpus Store Manager."""
        self.client.get(TestingConfig.SERVER_URI_CSM, query_string=dict(urn=Mocks.urn_custom))
        data_dict: dict = dict(title=Mocks.exercise.urn, annotations=Mocks.exercise.conll, aqls=Mocks.aqls,
                               exercise_type=ExerciseType.cloze.name, search_phenomena=[Phenomenon.partOfSpeech.name])
        first_response: Response = self.client.post(TestingConfig.SERVER_URI_CSM, data=json.dumps(data_dict))
        # ANNIS does not create deterministically reproducible results, so we only test for a substring
        self.assertIn(Mocks.graph_data_raw_part, first_response.data.decode("utf-8"))
        third_response: Response = self.client.post(TestingConfig.SERVER_URI_CSM, data=data_dict)
        # Response: Bad Request
        self.assertEqual(third_response.status_code, 400)

    def test_full_init(self):
        """ Fully initializes the application, including logging."""
        self.app.config["TESTING"] = False
        with patch.object(CorpusService, "init_graphannis_logging"):
            with patch.object(mcserver.app, "start_updater") as updater_mock:
                full_init(self.app, True)
                self.assertEqual(updater_mock.call_count, 1)
        self.app.config["TESTING"] = True

    def test_get_annotations_from_string(self):
        """ Gets annotation data from a given string, be it a CoNLL string or a corpus URN. """
        conll: List[TokenList]
        with patch.object(AnnotationService, "get_udpipe", return_value=Mocks.udpipe_string):
            with patch.object(CorpusService, "load_text_list", return_value=Mocks.text_list):
                with patch.object(CorpusService, "get_raw_text", return_value=Mocks.raw_text):
                    conll = CorpusService.get_annotations_from_string(Mocks.urn)
                    self.assertEqual(len(conll[0]), 4)
                mdg: MultiDiGraph = CorpusService.get_graph(Mocks.urn)
                self.assertEqual(len(mdg.nodes), 7)
                mdg = CorpusService.get_graph(f"{Mocks.urn}@1-1")
                self.assertEqual(len(mdg.nodes), 7)
        with patch.object(CustomCorpusService, "get_treebank_annotations", return_value=Mocks.annotations):
            conll = CorpusService.get_annotations_from_string(Mocks.urn_custom)
            self.assertEqual(len(conll[0]), 6)
        with patch.object(CustomCorpusService, "get_custom_corpus_annotations", return_value=Mocks.annotations * 2):
            urn: str = f"{Config.CUSTOM_CORPUS_VIVA_URN}:1.1-1.1"
            conll = CorpusService.get_annotations_from_string(urn)
            self.assertEqual(len(conll), 2)

    def test_get_frequency_analysis(self):
        """ Gets a frequency analysis by calling the CSM. """
        with patch.object(mcserver.app.services.corpusService.requests, "get", return_value=MockResponse(
                json.dumps([FrequencyItem(values=[], phenomena=[], count=[]).serialize()]))):
            fa: FrequencyAnalysis = CorpusService.get_frequency_analysis(urn=Mocks.urn_custom, is_csm=False)
            self.assertEqual(len(fa), 1)
        CorpusService.get_corpus(Mocks.urn_custom, True)
        with patch.object(CorpusService, "get_corpus", return_value=Mocks.annis_response):
            fa = CorpusService.get_frequency_analysis(Mocks.urn_custom, True)
            self.assertEqual(len(fa), 242)

    def test_get_graph(self):
        """ Retrieves a graph from the cache or, if not there, builds it from scratch. """
        expected_mdg: MultiDiGraph = MultiDiGraph([(1, 2), (2, 3), (3, 4)])
        with patch.object(Config.CORPUS_STORAGE_MANAGER, "subcorpus_graph", return_value=expected_mdg):
            mdg: MultiDiGraph = CorpusService.get_graph(Mocks.urn)
            self.assertEqual(mdg, expected_mdg)

    def test_init_updater(self):
        """Initializes the corpus list updater."""
        with patch.object(DatabaseService, 'check_corpus_list_age', side_effect=OperationalError("", [], "")):
            ui_cts: UpdateInfo = UpdateInfo(resource_type=ResourceType.cts_data,
                                            last_modified_time=datetime.fromtimestamp(1))
            db.session.add(ui_cts)
            db.session.commit()
            with patch.object(CorpusService, 'update_corpora') as update_mock:
                t: Thread = start_updater(self.app)
                self.assertIsInstance(t, Thread)
                self.assertTrue(t.is_alive())
                time.sleep(0.1)
                UpdateInfo.query.delete()
                assert not update_mock.called

    def test_process_corpus_data(self):
        """Builds a graph from annotated text data."""
        disk_urn: str = AnnotationService.get_disk_urn(Mocks.urn_custom)
        AnnotationService.map_conll_to_graph(corpus_name=Mocks.urn_custom, conll=Mocks.annotations,
                                             cs=Config.CORPUS_STORAGE_MANAGER, file_name=disk_urn)
        result: dict = CorpusService.process_corpus_data(urn=Mocks.urn_custom, annotations=Mocks.annotations,
                                                         aqls=["upostag"], exercise_type=ExerciseType.cloze,
                                                         search_phenomena=[Phenomenon.partOfSpeech])
        gd: GraphData = AnnotationService.map_graph_data(result["graph_data_raw"])
        self.assertEqual(len(gd.nodes), len(Mocks.nodes))
        text_parts_list: List[Tuple[str, str]] = CorpusService.load_text_list(Mocks.urn_custom)
        self.assertEqual(len(text_parts_list), 1)

    def test_run_app(self):
        """ Creates a new app and runs it. """
        with patch.object(csm, "get_app") as mock_get_app:
            csm.run_app()
            self.assertEqual(mock_get_app.call_count, 1)


class CommonTestCase(unittest.TestCase):
    def setUp(self):
        """Initializes the testing environment."""
        self.start_time = time.time()
        if os.path.exists(Config.GRAPH_DATABASE_DIR):
            shutil.rmtree(Config.GRAPH_DATABASE_DIR)
        with patch.object(TextService, "init_stop_words_latin"):
            self.app: Flask = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        """Finishes testing by removing the traces."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        print("{0}: {1} seconds".format(self.id(), "%.2f" % (time.time() - self.start_time)))

    def test_add_edges(self):
        """Adds edges to an existing graph based on a list of keys and constraints to their similarity and frequency."""
        w2v: Word2Vec = Word2Vec([x.split() for x in Mocks.raw_text.split(". ")], min_count=1, sample=0)
        graph: Graph = Graph()
        add_edges(["fortis"], w2v, 2, 1, graph)
        self.assertGreater(len(graph.edges), 1)

    def test_add_urn_to_sentences(self):
        """ Adds the relevant URN for every annotated sentence. """
        conll: List[TokenList] = copy.deepcopy(Mocks.annotations)
        text_list: List[Tuple[str, str]] = [(Mocks.urn, conll[0].tokens[0]["form"]), (Mocks.urn_custom, "")]
        conll[0].tokens[0]["form"] += "."
        conll.append(TokenList(tokens=[
            {"id": 1, "form": "Caesar.", "lemma": "Caeso", "upostag": "VERB", "xpostag": "L3|modJ|tem3|gen4|stAV",
             "feats": {"Mood": "Ind", "Number": "Sing", "Person": "1", "Tense": "Fut", "VerbForm": "Fin",
                       "Voice": "Pass"}, "head": 0, "deprel": "root", "deps": None, "misc": {"ref": "1.1"}}],
            metadata=OrderedDict([("sent_id", "2"), ("urn", "")])))
        AnnotationService.add_urn_to_sentences(text_list, conll)
        self.assertEqual(conll[0].metadata["urn"], Mocks.urn)
        self.assertEqual(conll[1].metadata["urn"], "")

    def test_create_xml_string(self):
        """Exports the exercise data to the Moodle XML format. See https://docs.moodle.org/35/en/Moodle_XML_format ."""
        xml_string: str = XMLservice.create_xml_string(Exercise(exercise_type=ExerciseType.matching.value), [],
                                                       FileType.pdf, [])
        self.assertEqual(xml_string, Mocks.exercise_xml)

    def test_extract_custom_corpus_text(self):
        """ Extracts text from the relevant parts of a (custom) corpus. """
        new_text_parts: List[Tuple[str, str]] = CustomCorpusService.extract_custom_corpus_text(
            Mocks.text_parts, ["", ""], ["", "0"], "", 1, [False, True])
        self.assertEqual(len(new_text_parts), 0)
        new_text_parts = CustomCorpusService.extract_custom_corpus_text(Mocks.text_parts, ["", ""], ["", "0"], "", 1)
        self.assertEqual(new_text_parts[0][1], Mocks.text_parts[0].text_value)
        new_text_parts = CustomCorpusService.extract_custom_corpus_text(Mocks.text_parts, ["1"], ["3"], "")
        self.assertEqual(new_text_parts[0][1], Mocks.text_parts[0].text_value)

    def test_find_matches(self):
        """ Finds matches for a given URN and AQL and returns the corresponding node IDs. """
        expected_matches: List[str] = ["a", "b"]
        with patch.object(mcserver.app.services.corpusService.requests, "get",
                          return_value=MockResponse(json.dumps(expected_matches))):
            matches: List[str] = CorpusService.find_matches(Mocks.urn, "")
            self.assertEqual(matches, expected_matches)

    def test_get_concept_network(self):
        """Extracts a network of words from vector data in an AI model."""
        with patch.object(mcserver.app.api.vectorNetworkAPI, "add_edges", side_effect=Mocks.mock_add_eges):
            with patch.object(mcserver.app.api.vectorNetworkAPI.Word2Vec, "load", return_value=MockW2V()):
                svg_string: str = get_concept_network("ueritas", highlight_regex_string="uera")
                self.assertGreater(len(svg_string), 6500)

    def test_get_corpus(self):
        """ Loads the text for a standard corpus from the CTS API or cache. """
        ar: AnnisResponse = CorpusService.get_corpus("", True)
        self.assertEqual(len(ar.nodes), 0)

    def test_get_custom_corpus_annotations(self):
        """ Retrieves the annotated text for a custom non-PROIEL corpus, e.g. a textbook. """
        mock_conll: List[TokenList] = Mocks.annotations + [TokenList([], metadata=OrderedDict([("sent_id", "3")]))]
        with patch.object(CustomCorpusService, "get_custom_corpus_text", return_value=Mocks.text_list):
            with patch.object(AnnotationService, "get_udpipe", return_value=Mocks.udpipe_string):
                with patch.object(AnnotationService, "parse_conll_string", return_value=mock_conll):
                    conll: List[TokenList] = CustomCorpusService.get_custom_corpus_annotations(Mocks.urn + "@1-2")
                    self.assertEqual(len(conll), 1)

    def test_get_custom_corpus_reff(self):
        """ Retrieves possible citations for given URN. """
        CustomCorpusService.custom_corpora[4].text_parts = Mocks.text_parts
        reff: List[str] = CustomCorpusService.get_custom_corpus_reff(Mocks.urn_custom[:-15])
        self.assertEqual(len(reff), 0)
        McTestCase.clear_folder(Config.REFF_CACHE_DIRECTORY)
        reff = CustomCorpusService.get_custom_corpus_reff(Mocks.urn_custom[:-14])
        self.assertEqual(len(reff), 1)
        McTestCase.clear_folder(Config.REFF_CACHE_DIRECTORY)
        reff = CustomCorpusService.get_custom_corpus_reff(Mocks.urn_custom[:-9])
        self.assertEqual(len(reff), 2)
        reff = CustomCorpusService.get_custom_corpus_reff(Mocks.urn_custom[:-9])
        self.assertEqual(len(reff), 2)
        McTestCase.clear_folder(Config.REFF_CACHE_DIRECTORY)

    def test_get_custom_corpus_text(self):
        """ Retrieves the text for a custom corpus, e.g. a textbook. """
        text_list: List[Tuple[str, str]] = CustomCorpusService.get_custom_corpus_text(Mocks.urn)
        self.assertEqual(len(text_list), 0)

    def test_get_pdf_html_string(self):
        """ Builds an HTML string from an exercise, e.g. to construct a PDF from it. """
        Mocks.exercise.exercise_type = ExerciseType.matching.value
        solutions: List[Solution] = [Solution(json_dict=x) for x in json.loads(Mocks.exercise.solutions)]
        result: str = FileService.get_pdf_html_string(Mocks.exercise, Mocks.annotations, FileType.pdf, solutions)
        self.assertEqual(result, '<br><p>: </p><p><table><tr><td>praecepturus</td><td>Caesar</td></tr></table></p>')
        Mocks.exercise.exercise_type = ExerciseType.markWords.value
        result = FileService.get_pdf_html_string(Mocks.exercise, Mocks.annotations, FileType.pdf, solutions)
        self.assertEqual(result, '<p>: </p><p>Caesar et Galli fortes sunt.</p><br><br>')
        Mocks.exercise.exercise_type = ExerciseType.cloze.value

    def test_get_raw_text(self):
        """ Retrieves the raw text for a corpus. """
        with patch.object(CorpusService, "get_corpus", return_value=Mocks.annis_response):
            text: str = CorpusService.get_raw_text(Mocks.urn, True)
            self.assertEqual(len(text), 349)

    def test_get_solutions_by_index(self):
        """ If available, makes use of the solution indices to return only the wanted solutions. """
        solutions: List[Solution] = TextService.get_solutions_by_index(Mocks.exercise)
        self.assertEqual(len(solutions), 1)

    def test_get_treebank_annotations(self):
        """ Retrieves annotations from a treebank. """
        cache_path: str = os.path.join(Config.TREEBANKS_CACHE_DIRECTORY,
                                       ntpath.basename(CustomCorpusService.custom_corpora[4].file_path) + ".json")
        if os.path.exists(cache_path):
            os.remove(cache_path)
        with patch.object(mcserver.app.services.customCorpusService.conllu, "parse",
                          return_value=Mocks.annotations) as parse_mock:
            with patch.object(CustomCorpusService, "get_treebank_sub_annotations", return_value=Mocks.annotations):
                conll: List[TokenList] = CustomCorpusService.get_treebank_annotations(Mocks.urn_custom)
                self.assertIs(conll, Mocks.annotations)
                with patch.object(mcserver.app.services.customCorpusService.json, "loads", side_effect=ValueError):
                    conll = CustomCorpusService.get_treebank_annotations(Mocks.urn_custom)
                    os.remove(cache_path)
                    self.assertEqual(parse_mock.call_count, 2)

    def test_get_treebank_sub_annotations(self):
        """ Retrieves annotations for nested parts of a treebank. """
        annotations: List[TokenList] = Mocks.annotations + [TokenList([], metadata=OrderedDict([("sent_id", "2")])),
                                                            TokenList([], metadata=OrderedDict([("sent_id", "3")]))]
        conll: List[TokenList] = CustomCorpusService.get_treebank_sub_annotations(
            Mocks.urn + "@1-3", annotations, CustomCorpusService.custom_corpora[4])
        self.assertEqual(len(conll), 3)
        cc: CustomCorpus = CustomCorpusService.custom_corpora[-1]
        urn: str = cc.corpus.source_urn + ":1.1-1.2"
        conll = CustomCorpusService.get_treebank_sub_annotations(urn, [], cc)
        self.assertEqual(len(cc.text_parts), 2)

    def test_get_udpipe(self):
        """Annotates a single text with UdPipe. The beginning of the CONLL has to be left out because it contains the
        randomly generated temp file path and thus cannot be predicted exactly."""
        text = "Caesar fortis est. Galli moriuntur."
        conll = AnnotationService.get_udpipe(text)
        self.assertIn(Mocks.udpipe_string, conll)

    def test_init_custom_corpus(self):
        """Adds custom corpora to the corpus list, e.g. the PROIEL corpora."""
        with patch.object(CustomCorpusService, "get_treebank_annotations", return_value=Mocks.annotations):
            cc: CustomCorpus = CustomCorpusService.init_custom_corpus(CustomCorpusService.custom_corpora[0])
            self.assertEqual(len(cc.text_parts), 1)

    def test_init_db_alembic(self):
        """ In Docker, the alembic version is not initially written to the database, so we need to set it manually. """
        db.engine.execute(f"DROP TABLE {Config.DATABASE_TABLE_ALEMBIC}")
        self.assertEqual(db.engine.dialect.has_table(db.engine, Config.DATABASE_TABLE_ALEMBIC), False)
        DatabaseService.init_db_alembic()
        self.assertEqual(db.engine.dialect.has_table(db.engine, Config.DATABASE_TABLE_ALEMBIC), True)

    def test_init_db_corpus(self):
        """Initializes the corpus table."""
        cc: CustomCorpus = CustomCorpusService.custom_corpora[0]
        old_corpus: Corpus = Mocks.corpora[0]
        old_corpus.source_urn = cc.corpus.source_urn
        McTestCase.add_corpus(old_corpus)
        del old_corpus
        DatabaseService.init_db_corpus()
        corpus: Corpus = Corpus.query.filter_by(source_urn=cc.corpus.source_urn).first()
        self.assertEqual(corpus.title, cc.corpus.title)
        Corpus.query.delete()

    def test_init_stop_words_latin(self):
        """Initializes the stop words list for Latin texts and caches it if necessary."""

        def clear_cache():
            if os.path.exists(Config.STOP_WORDS_LATIN_PATH):
                os.remove(Config.STOP_WORDS_LATIN_PATH)

        clear_cache()
        stop_word_list: Dict[str, List[str]] = {"a": ["b"]}
        mr: MockResponse = MockResponse(json.dumps(stop_word_list))
        with patch.object(mcserver.app.services.textService.requests, "get", return_value=mr) as mock_get_request:
            TextService.init_stop_words_latin()
            self.assertEqual(len(TextService.stop_words_latin), 1)
            TextService.init_stop_words_latin()
            clear_cache()
            self.assertEqual(mock_get_request.call_count, 1)

    def test_load_text_list(self):
        """ Loads the text list for a new corpus. """
        with patch.object(mcserver.app.services.corpusService.HttpCtsRetriever, 'getPassage',
                          return_value=Mocks.cts_passage_xml) as get_passage_mock:
            text_parts: List[Tuple[str, str]] = CorpusService.load_text_list(Mocks.urn)
            self.assertEqual(len(text_parts), 2)
            get_passage_mock.return_value = Mocks.cts_passage_xml_2_levels
            text_parts = CorpusService.load_text_list(Mocks.urn[:-8] + "-1.1")
            self.assertEqual(len(text_parts), 1)
            get_passage_mock.return_value = Mocks.cts_passage_xml_1_level
            text_parts = CorpusService.load_text_list(Mocks.urn[:-10] + "-3")
            self.assertEqual(len(text_parts), 3)
            get_passage_mock.side_effect = HTTPError()
            text_parts: List[Tuple[str, str]] = CorpusService.load_text_list(Mocks.urn)
            self.assertEqual(text_parts, [])

    def test_make_docx_file(self):
        """ Saves an exercise to a DOCX file (e.g. for later download). """
        file_path: str = os.path.join(Config.TMP_DIRECTORY, "make_docx_file.docx")
        solutions: List[Solution] = [Solution(json_dict=x) for x in json.loads(Mocks.exercise.solutions)]
        FileService.make_docx_file(Mocks.exercise, file_path, Mocks.annotations, FileType.docx, solutions)
        self.assertEqual(os.path.getsize(file_path), 36611)
        Mocks.exercise.exercise_type = ExerciseType.markWords.value
        FileService.make_docx_file(Mocks.exercise, file_path, Mocks.annotations, FileType.docx, solutions)
        self.assertEqual(os.path.getsize(file_path), 36599)
        Mocks.exercise.exercise_type = ExerciseType.matching.value
        FileService.make_docx_file(Mocks.exercise, file_path, Mocks.annotations, FileType.docx, solutions)
        self.assertEqual(os.path.getsize(file_path), 36714)
        Mocks.exercise.exercise_type = ExerciseType.cloze.value
        os.remove(file_path)

    def test_make_tmp_file_from_exercise(self):
        """ Creates a temporary file from a given exercise, e.g. for downloading. """
        df: DownloadableFile = FileService.make_tmp_file_from_exercise(FileType.xml, Mocks.exercise, [0])
        self.assertTrue(os.path.exists(df.file_path))
        os.remove(df.file_path)
        df: DownloadableFile = FileService.make_tmp_file_from_exercise(FileType.docx, Mocks.exercise, [0])
        self.assertTrue(os.path.exists(df.file_path))
        os.remove(df.file_path)

    def test_make_tmp_file_from_html(self):
        """ Creates a temporary file from a given HTML string, e.g. for downloading. """
        html: str = "<html lang='la'><p>test</p><span class='tok'><u>abc</u></span></html>"
        df: DownloadableFile = FileService.make_tmp_file_from_html(Mocks.urn_custom, FileType.pdf, html)
        self.assertTrue(os.path.exists(df.file_path))
        os.remove(df.file_path)
        df: DownloadableFile = FileService.make_tmp_file_from_html(Mocks.urn_custom, FileType.docx, html)
        self.assertTrue(os.path.exists(df.file_path))
        os.remove(df.file_path)

    def test_map_graph_data(self):
        """Maps graph data to exercise data."""
        ed_expected: ExerciseData = Mocks.exercise_data
        node_expected: NodeMC = ed_expected.graph.nodes[0]
        node = {"id": node_expected.id, "annis::node_name": node_expected.annis_node_name,
                "annis::node_type": node_expected.annis_node_type, "annis::tok": node_expected.annis_tok,
                "annis::type": node_expected.annis_type, "udep::lemma": node_expected.udep_lemma,
                "udep::upostag": node_expected.udep_upostag, "udep::xpostag": node_expected.udep_xpostag}
        link_expected: LinkMC = ed_expected.graph.links[0]
        link = {"source": link_expected.source, "target": link_expected.target,
                "annis::component_name": link_expected.annis_component_name,
                "annis::component_type": link_expected.annis_component_type, "udep::deprel": link_expected.udep_deprel}
        graph_data_raw: Dict = dict(directed=ed_expected.graph.directed, graph=ed_expected.graph.graph,
                                    multigraph=ed_expected.graph.multigraph, links=[link], nodes=[node])
        gd: GraphData = AnnotationService.map_graph_data(graph_data_raw=graph_data_raw)
        self.assertEqual(gd.graph, ed_expected.graph.graph)
        self.assertEqual(gd.multigraph, ed_expected.graph.multigraph)
        self.assertEqual(gd.directed, ed_expected.graph.directed)
        self.assertEqual(gd.nodes[0], ed_expected.graph.nodes[0])
        self.assertEqual(gd.links[0], ed_expected.graph.links[0])

    def test_models(self):
        """ Tests various models and their specific methods. """
        self.assertFalse(Mocks.corpora[0] == Mocks.corpora[1])
        self.assertFalse(Mocks.corpora[0] == "")
        self.assertTrue(Mocks.exercise.__repr__().startswith("<Exercise"))
        ui: UpdateInfo = UpdateInfo(ResourceType.cts_data)
        self.assertTrue(ui.__repr__().startswith("<UpdateInfo"))
        del ui
        gd: GraphData = AnnotationService.map_graph_data(Mocks.annis_response_dict["graph_data_raw"])
        self.assertFalse(gd.links[0] == gd.links[1])
        self.assertFalse(gd.links[0] == "")
        self.assertFalse(gd.nodes[0] == gd.nodes[1])
        self.assertFalse(gd.nodes[0] == "")
        choice_dict: dict = dict(id="", description={"en-US": "desc"})
        self.assertEqual(Choice(choice_dict).serialize(), choice_dict)
        xapi: XapiStatement = XapiStatement(json.loads(Mocks.xapi_json_string)["0"])
        self.assertEqual(len(xapi.serialize().keys()), 5)
        session.make_transient(Mocks.corpora[0])
        session.make_transient(Mocks.exercise)

    def test_sort_nodes(self):
        """Sorts the nodes according to the ordering links, i.e. by their tokens' occurrence in the text."""
        old_graph_data: GraphData = GraphData(nodes=[])
        new_graph_data: GraphData = AnnotationService.sort_nodes(old_graph_data)
        self.assertIs(old_graph_data, new_graph_data)

    def test_strip_name_spaces(self):
        """Removes all namespaces from an XML document for easier parsing, e.g. with XPath."""
        xml: etree._Element = etree.Element("{namespace}root")
        child: etree._Element = etree.Element("{namespace}child")
        xml.append(child)
        with patch("mcserver.app.services.xmlService.hasattr", return_value=False) as has_attr_mock:
            XMLservice.strip_name_spaces(xml)
            self.assertEqual(len(child.tag), 16)
            has_attr_mock.return_value = True
            XMLservice.strip_name_spaces(xml)
            self.assertEqual(len(child.tag), 5)

    def test_start_updater(self):
        """Starts an updater thread."""
        t: Thread = start_updater(self.app)
        self.assertIsInstance(t, Thread)
        self.assertTrue(t.is_alive())

    def test_update_exercises(self):
        """Deletes old exercises."""
        exercises: List[Exercise] = \
            [Exercise(last_access_time=datetime.utcnow(), urn="urn", solutions="[]", uri="uri1", eid="eid1"),
             Exercise(last_access_time=datetime.utcnow(), urn="urn", solutions=json.dumps([Solution().serialize()]),
                      text_complexity=0, uri="uri2", eid="eid2")]
        db.session.add_all(exercises)
        db.session.commit()

        with patch.object(mcserver.app.services.textComplexityService.requests, "post",
                          return_value=MockResponse(Mocks.text_complexity_json_string)):
            with patch.object(CorpusService, "get_corpus", return_value=Mocks.annis_response):
                DatabaseService.update_exercises(False)
                exercises = Exercise.query.all()
                self.assertEqual(len(exercises), 1)
                self.assertEqual(exercises[0].text_complexity, 54.53)
        Exercise.query.delete()


if __name__ == '__main__':
    runner: unittest.TextTestRunner = unittest.TextTestRunner()
    suite: unittest.TestSuite = unittest.TestSuite()
    suite.addTests(TestLoader().loadTestsFromTestCase(McTestCase))
    suite.addTests(TestLoader().loadTestsFromTestCase(CsmTestCase))
    suite.addTests(TestLoader().loadTestsFromTestCase(CommonTestCase))
    runner.run(suite)
    # delete the SQLITE database to have a clean start next time
    os.remove(TestingConfig.SQLALCHEMY_DATABASE_URI[10:])
