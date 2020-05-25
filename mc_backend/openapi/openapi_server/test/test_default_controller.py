# coding: utf-8

from __future__ import absolute_import
import unittest

from flask import json
from six import BytesIO

from openapi.openapi_server.models.corpus import Corpus  # noqa: E501
from openapi.openapi_server.models.exercise_base import ExerciseBase  # noqa: E501
from openapi.openapi_server.models.inline_response200 import InlineResponse200  # noqa: E501
from openapi.openapi_server.models.unknownbasetype import UNKNOWN_BASE_TYPE  # noqa: E501
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
        unknown_base_type = {}
        headers = { 
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        response = self.client.open(
            '/mc/api/v1.0/exercise',
            method='POST',
            headers=headers,
            data=json.dumps(unknown_base_type),
            content_type='application/x-www-form-urlencoded')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
