# coding: utf-8

from __future__ import absolute_import
import unittest

from flask import json
from six import BytesIO

from openapi.openapi_server.models.annis_response import AnnisResponse  # noqa: E501
from openapi.openapi_server.models.corpus import Corpus  # noqa: E501
from openapi.openapi_server.models.file_type import FileType  # noqa: E501
from openapi.openapi_server.models.frequency_item import FrequencyItem  # noqa: E501
from openapi.openapi_server.models.matching_exercise import MatchingExercise  # noqa: E501
from openapi.openapi_server.models.sentence import Sentence  # noqa: E501
from openapi.openapi_server.models.static_exercise import StaticExercise  # noqa: E501
from openapi.openapi_server.models.text_complexity import TextComplexity  # noqa: E501
from openapi.openapi_server.models.vocabulary_mc import VocabularyMC  # noqa: E501
from openapi.openapi_server.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_mcserver_app_api_corpus_api_delete(self):
        """Test case for mcserver_app_api_corpus_api_delete

        Deletes a single corpus by ID.
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/mc/api/v1.0/corpora/{cid}'.format(cid=1),
            method='DELETE',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_mcserver_app_api_corpus_api_get(self):
        """Test case for mcserver_app_api_corpus_api_get

        Returns a single corpus by ID.
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/mc/api/v1.0/corpora/{cid}'.format(cid=1),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_mcserver_app_api_corpus_api_patch(self):
        """Test case for mcserver_app_api_corpus_api_patch

        Updates a single corpus by ID.
        """
        query_string = [('author', Aulus Gellius),
                        ('source_urn', urn:cts:latinLit:phi1254.phi001.perseus-lat2),
                        ('title', Noctes Atticae)]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/mc/api/v1.0/corpora/{cid}'.format(cid=1),
            method='PATCH',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_mcserver_app_api_corpus_list_api_get(self):
        """Test case for mcserver_app_api_corpus_list_api_get

        Returns a list of corpora.
        """
        query_string = [('last_update_time', 123456789)]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/mc/api/v1.0/corpora',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_mcserver_app_api_exercise_api_get(self):
        """Test case for mcserver_app_api_exercise_api_get

        Returns exercise data by ID.
        """
        query_string = [('eid', 12345678-1234-5678-1234-567812345678)]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/mc/api/v1.0/exercise',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    @unittest.skip("application/x-www-form-urlencoded not supported by Connexion")
    def test_mcserver_app_api_exercise_api_post(self):
        """Test case for mcserver_app_api_exercise_api_post

        Creates a new exercise.
        """
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        response = self.client.open(
            '/mc/api/v1.0/exercise',
            method='POST',
            headers=headers,
            content_type='application/x-www-form-urlencoded')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_mcserver_app_api_exercise_list_api_get(self):
        """Test case for mcserver_app_api_exercise_list_api_get

        Provides metadata for all available exercises.
        """
        query_string = [('lang', en),
                        ('frequency_upper_bound', 500),
                        ('last_update_time', 123456789),
                        ('vocabulary', {})]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/mc/api/v1.0/exerciseList',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_mcserver_app_api_file_api_get(self):
        """Test case for mcserver_app_api_file_api_get

        Provides the URL to download a specific file.
        """
        query_string = [('id', 12345678-1234-5678-1234-567812345678),
                        ('type', {}),
                        ('solution_indices', 56)]
        headers = { 
            'Accept': 'application/xml',
        }
        response = self.client.open(
            '/mc/api/v1.0/file',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    @unittest.skip("application/x-www-form-urlencoded not supported by Connexion")
    def test_mcserver_app_api_file_api_post(self):
        """Test case for mcserver_app_api_file_api_post

        Serializes and persists learning results or HTML content for later access.
        """
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        data = dict(file_type={},
                    html_content='html_content_example',
                    learning_result='learning_result_example',
                    urn='urn_example')
        response = self.client.open(
            '/mc/api/v1.0/file',
            method='POST',
            headers=headers,
            data=data,
            content_type='application/x-www-form-urlencoded')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_mcserver_app_api_frequency_api_get(self):
        """Test case for mcserver_app_api_frequency_api_get

        Returns results for a frequency query from ANNIS for a given CTS URN.
        """
        query_string = [('urn', urn:cts:latinLit:phi1254.phi001.perseus-lat2:5.6.21-5.6.21)]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/mc/api/v1.0/frequency',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_mcserver_app_api_h5p_api_get(self):
        """Test case for mcserver_app_api_h5p_api_get

        Provides JSON templates for client-side H5P exercise layouts.
        """
        query_string = [('eid', 12345678-1234-5678-1234-567812345678),
                        ('lang', en),
                        ('solution_indices', 56)]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/mc/api/v1.0/h5p',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    @unittest.skip("application/x-www-form-urlencoded not supported by Connexion")
    def test_mcserver_app_api_kwic_api_post(self):
        """Test case for mcserver_app_api_kwic_api_post

        Provides example contexts for a given phenomenon in a given corpus.
        """
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        data = dict(search_values='[]',
                    urn='urn_example',
                    ctx_left=56,
                    ctx_right=56)
        response = self.client.open(
            '/mc/api/v1.0/kwic',
            method='POST',
            headers=headers,
            data=data,
            content_type='application/x-www-form-urlencoded')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_mcserver_app_api_raw_text_api_get(self):
        """Test case for mcserver_app_api_raw_text_api_get

        Provides the raw text for a requested text passage.
        """
        query_string = [('urn', urn:cts:latinLit:phi1254.phi001.perseus-lat2:5.6.21-5.6.21)]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/mc/api/v1.0/rawtext',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_mcserver_app_api_static_exercises_api_get(self):
        """Test case for mcserver_app_api_static_exercises_api_get

        Returns metadata for static exercises.
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/mc/api/v1.0/staticExercises',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_mcserver_app_api_textcomplexity_api_get(self):
        """Test case for mcserver_app_api_textcomplexity_api_get

        Gives users measures of text complexity for a given text.
        """
        query_string = [('measure', all),
                        ('urn', urn:cts:latinLit:phi1254.phi001.perseus-lat2:5.6.21-5.6.21)]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/mc/api/v1.0/textcomplexity',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_mcserver_app_api_valid_reff_api_get(self):
        """Test case for mcserver_app_api_valid_reff_api_get

        Gives users all the citable text references for a corpus.
        """
        query_string = [('urn', urn:cts:latinLit:phi1254.phi001.perseus-lat2:5.6.21-5.6.21)]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/mc/api/v1.0/validReff',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_mcserver_app_api_vector_network_api_get(self):
        """Test case for mcserver_app_api_vector_network_api_get

        Provides network data for the vectors in an AI model.
        """
        query_string = [('search_regex', 'search_regex_example'),
                        ('highlight_regex', ver[aoe]),
                        ('min_count', 3),
                        ('nearest_neighbor_count', 0)]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/mc/api/v1.0/vectorNetwork',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    @unittest.skip("application/x-www-form-urlencoded not supported by Connexion")
    def test_mcserver_app_api_vector_network_api_post(self):
        """Test case for mcserver_app_api_vector_network_api_post

        Provides network data for the vectors in an AI model.
        """
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        data = dict(search_regex='search_regex_example',
                    nearest_neighbor_count=0)
        response = self.client.open(
            '/mc/api/v1.0/vectorNetwork',
            method='POST',
            headers=headers,
            data=data,
            content_type='application/x-www-form-urlencoded')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_mcserver_app_api_vocabulary_api_get(self):
        """Test case for mcserver_app_api_vocabulary_api_get

        Shows how well the vocabulary of a text matches a predefined reference vocabulary.
        """
        query_string = [('frequency_upper_bound', 500),
                        ('query_urn', urn:cts:latinLit:phi0448.phi001.perseus-lat2:1.1.1-1.1.1),
                        ('vocabulary', {})]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/mc/api/v1.0/vocabulary',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    @unittest.skip("application/x-www-form-urlencoded not supported by Connexion")
    def test_mcserver_app_api_vocabulary_api_post(self):
        """Test case for mcserver_app_api_vocabulary_api_post

        Shows how well the vocabulary of a text matches a predefined reference vocabulary.
        """
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        data = dict(frequency_upper_bound=56,
                    query_urn='query_urn_example',
                    vocabulary={})
        response = self.client.open(
            '/mc/api/v1.0/vocabulary',
            method='POST',
            headers=headers,
            data=data,
            content_type='application/x-www-form-urlencoded')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
