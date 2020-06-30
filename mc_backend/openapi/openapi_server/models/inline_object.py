# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi.openapi_server.models.base_model_ import Model
from openapi.openapi_server.models.file_type import FileType
from openapi.openapi_server import util

from openapi.openapi_server.models.file_type import FileType  # noqa: E501

class InlineObject(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, file_type=None, html_content=None, learning_result=None, urn=None):  # noqa: E501
        """InlineObject - a model defined in OpenAPI

        :param file_type: The file_type of this InlineObject.  # noqa: E501
        :type file_type: FileType
        :param html_content: The html_content of this InlineObject.  # noqa: E501
        :type html_content: str
        :param learning_result: The learning_result of this InlineObject.  # noqa: E501
        :type learning_result: str
        :param urn: The urn of this InlineObject.  # noqa: E501
        :type urn: str
        """
        self.openapi_types = {
            'file_type': FileType,
            'html_content': str,
            'learning_result': str,
            'urn': str
        }

        self.attribute_map = {
            'file_type': 'file_type',
            'html_content': 'html_content',
            'learning_result': 'learning_result',
            'urn': 'urn'
        }

        self._file_type = file_type
        self._html_content = html_content
        self._learning_result = learning_result
        self._urn = urn

    @classmethod
    def from_dict(cls, dikt) -> 'InlineObject':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The inline_object of this InlineObject.  # noqa: E501
        :rtype: InlineObject
        """
        return util.deserialize_model(dikt, cls)

    @property
    def file_type(self):
        """Gets the file_type of this InlineObject.


        :return: The file_type of this InlineObject.
        :rtype: FileType
        """
        return self._file_type

    @file_type.setter
    def file_type(self, file_type):
        """Sets the file_type of this InlineObject.


        :param file_type: The file_type of this InlineObject.
        :type file_type: FileType
        """

        self._file_type = file_type

    @property
    def html_content(self):
        """Gets the html_content of this InlineObject.

        HTML content to be serialized.  # noqa: E501

        :return: The html_content of this InlineObject.
        :rtype: str
        """
        return self._html_content

    @html_content.setter
    def html_content(self, html_content):
        """Sets the html_content of this InlineObject.

        HTML content to be serialized.  # noqa: E501

        :param html_content: The html_content of this InlineObject.
        :type html_content: str
        """

        self._html_content = html_content

    @property
    def learning_result(self):
        """Gets the learning_result of this InlineObject.

        Serialized XAPI results for an interactive exercise.  # noqa: E501

        :return: The learning_result of this InlineObject.
        :rtype: str
        """
        return self._learning_result

    @learning_result.setter
    def learning_result(self, learning_result):
        """Sets the learning_result of this InlineObject.

        Serialized XAPI results for an interactive exercise.  # noqa: E501

        :param learning_result: The learning_result of this InlineObject.
        :type learning_result: str
        """

        self._learning_result = learning_result

    @property
    def urn(self):
        """Gets the urn of this InlineObject.

        CTS URN for the text passage from which the HTML content was created.  # noqa: E501

        :return: The urn of this InlineObject.
        :rtype: str
        """
        return self._urn

    @urn.setter
    def urn(self, urn):
        """Sets the urn of this InlineObject.

        CTS URN for the text passage from which the HTML content was created.  # noqa: E501

        :param urn: The urn of this InlineObject.
        :type urn: str
        """

        self._urn = urn