# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi.openapi_server.models.base_model_ import Model
from openapi.openapi_server.models.vocabulary_mc import VocabularyMC
from openapi.openapi_server import util

from openapi.openapi_server.models.vocabulary_mc import VocabularyMC  # noqa: E501

class VocabularyForm(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, frequency_upper_bound=None, query_urn=None, vocabulary=None):  # noqa: E501
        """VocabularyForm - a model defined in OpenAPI

        :param frequency_upper_bound: The frequency_upper_bound of this VocabularyForm.  # noqa: E501
        :type frequency_upper_bound: int
        :param query_urn: The query_urn of this VocabularyForm.  # noqa: E501
        :type query_urn: str
        :param vocabulary: The vocabulary of this VocabularyForm.  # noqa: E501
        :type vocabulary: VocabularyMC
        """
        self.openapi_types = {
            'frequency_upper_bound': int,
            'query_urn': str,
            'vocabulary': VocabularyMC
        }

        self.attribute_map = {
            'frequency_upper_bound': 'frequency_upper_bound',
            'query_urn': 'query_urn',
            'vocabulary': 'vocabulary'
        }

        self._frequency_upper_bound = frequency_upper_bound
        self._query_urn = query_urn
        self._vocabulary = vocabulary

    @classmethod
    def from_dict(cls, dikt) -> 'VocabularyForm':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The VocabularyForm of this VocabularyForm.  # noqa: E501
        :rtype: VocabularyForm
        """
        return util.deserialize_model(dikt, cls)

    @property
    def frequency_upper_bound(self):
        """Gets the frequency_upper_bound of this VocabularyForm.

        Upper bound for reference vocabulary frequency.  # noqa: E501

        :return: The frequency_upper_bound of this VocabularyForm.
        :rtype: int
        """
        return self._frequency_upper_bound

    @frequency_upper_bound.setter
    def frequency_upper_bound(self, frequency_upper_bound):
        """Sets the frequency_upper_bound of this VocabularyForm.

        Upper bound for reference vocabulary frequency.  # noqa: E501

        :param frequency_upper_bound: The frequency_upper_bound of this VocabularyForm.
        :type frequency_upper_bound: int
        """
        if frequency_upper_bound is None:
            raise ValueError("Invalid value for `frequency_upper_bound`, must not be `None`")  # noqa: E501

        self._frequency_upper_bound = frequency_upper_bound

    @property
    def query_urn(self):
        """Gets the query_urn of this VocabularyForm.

        URN for the query corpus.  # noqa: E501

        :return: The query_urn of this VocabularyForm.
        :rtype: str
        """
        return self._query_urn

    @query_urn.setter
    def query_urn(self, query_urn):
        """Sets the query_urn of this VocabularyForm.

        URN for the query corpus.  # noqa: E501

        :param query_urn: The query_urn of this VocabularyForm.
        :type query_urn: str
        """
        if query_urn is None:
            raise ValueError("Invalid value for `query_urn`, must not be `None`")  # noqa: E501

        self._query_urn = query_urn

    @property
    def vocabulary(self):
        """Gets the vocabulary of this VocabularyForm.


        :return: The vocabulary of this VocabularyForm.
        :rtype: VocabularyMC
        """
        return self._vocabulary

    @vocabulary.setter
    def vocabulary(self, vocabulary):
        """Sets the vocabulary of this VocabularyForm.


        :param vocabulary: The vocabulary of this VocabularyForm.
        :type vocabulary: VocabularyMC
        """
        if vocabulary is None:
            raise ValueError("Invalid value for `vocabulary`, must not be `None`")  # noqa: E501

        self._vocabulary = vocabulary
