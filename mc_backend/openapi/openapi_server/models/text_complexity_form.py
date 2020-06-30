# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi.openapi_server.models.base_model_ import Model
from openapi.openapi_server import util


class TextComplexityForm(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, measure=None, urn=None, annis_response=None):  # noqa: E501
        """TextComplexityForm - a model defined in OpenAPI

        :param measure: The measure of this TextComplexityForm.  # noqa: E501
        :type measure: str
        :param urn: The urn of this TextComplexityForm.  # noqa: E501
        :type urn: str
        :param annis_response: The annis_response of this TextComplexityForm.  # noqa: E501
        :type annis_response: str
        """
        self.openapi_types = {
            'measure': str,
            'urn': str,
            'annis_response': str
        }

        self.attribute_map = {
            'measure': 'measure',
            'urn': 'urn',
            'annis_response': 'annis_response'
        }

        self._measure = measure
        self._urn = urn
        self._annis_response = annis_response

    @classmethod
    def from_dict(cls, dikt) -> 'TextComplexityForm':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The TextComplexityForm of this TextComplexityForm.  # noqa: E501
        :rtype: TextComplexityForm
        """
        return util.deserialize_model(dikt, cls)

    @property
    def measure(self):
        """Gets the measure of this TextComplexityForm.

        Label of the desired measure for text complexity.  # noqa: E501

        :return: The measure of this TextComplexityForm.
        :rtype: str
        """
        return self._measure

    @measure.setter
    def measure(self, measure):
        """Sets the measure of this TextComplexityForm.

        Label of the desired measure for text complexity.  # noqa: E501

        :param measure: The measure of this TextComplexityForm.
        :type measure: str
        """
        if measure is None:
            raise ValueError("Invalid value for `measure`, must not be `None`")  # noqa: E501

        self._measure = measure

    @property
    def urn(self):
        """Gets the urn of this TextComplexityForm.

        CTS URN for the text passage from which the text complexity should be calculated.  # noqa: E501

        :return: The urn of this TextComplexityForm.
        :rtype: str
        """
        return self._urn

    @urn.setter
    def urn(self, urn):
        """Sets the urn of this TextComplexityForm.

        CTS URN for the text passage from which the text complexity should be calculated.  # noqa: E501

        :param urn: The urn of this TextComplexityForm.
        :type urn: str
        """
        if urn is None:
            raise ValueError("Invalid value for `urn`, must not be `None`")  # noqa: E501

        self._urn = urn

    @property
    def annis_response(self):
        """Gets the annis_response of this TextComplexityForm.

        Serialized ANNIS response.  # noqa: E501

        :return: The annis_response of this TextComplexityForm.
        :rtype: str
        """
        return self._annis_response

    @annis_response.setter
    def annis_response(self, annis_response):
        """Sets the annis_response of this TextComplexityForm.

        Serialized ANNIS response.  # noqa: E501

        :param annis_response: The annis_response of this TextComplexityForm.
        :type annis_response: str
        """

        self._annis_response = annis_response