# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi.openapi_server.models.base_model_ import Model
from openapi.openapi_server import util


class SolutionElement(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, content=None, salt_id=None, sentence_id=None, token_id=None):  # noqa: E501
        """SolutionElement - a model defined in OpenAPI

        :param content: The content of this SolutionElement.  # noqa: E501
        :type content: str
        :param salt_id: The salt_id of this SolutionElement.  # noqa: E501
        :type salt_id: str
        :param sentence_id: The sentence_id of this SolutionElement.  # noqa: E501
        :type sentence_id: int
        :param token_id: The token_id of this SolutionElement.  # noqa: E501
        :type token_id: int
        """
        self.openapi_types = {
            'content': str,
            'salt_id': str,
            'sentence_id': int,
            'token_id': int
        }

        self.attribute_map = {
            'content': 'content',
            'salt_id': 'salt_id',
            'sentence_id': 'sentence_id',
            'token_id': 'token_id'
        }

        self._content = content
        self._salt_id = salt_id
        self._sentence_id = sentence_id
        self._token_id = token_id

    @classmethod
    def from_dict(cls, dikt) -> 'SolutionElement':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The SolutionElement of this SolutionElement.  # noqa: E501
        :rtype: SolutionElement
        """
        return util.deserialize_model(dikt, cls)

    @property
    def content(self):
        """Gets the content of this SolutionElement.

        Content of the solution element.  # noqa: E501

        :return: The content of this SolutionElement.
        :rtype: str
        """
        return self._content

    @content.setter
    def content(self, content):
        """Sets the content of this SolutionElement.

        Content of the solution element.  # noqa: E501

        :param content: The content of this SolutionElement.
        :type content: str
        """

        self._content = content

    @property
    def salt_id(self):
        """Gets the salt_id of this SolutionElement.

        Unique identifier for the node in the SALT model.  # noqa: E501

        :return: The salt_id of this SolutionElement.
        :rtype: str
        """
        return self._salt_id

    @salt_id.setter
    def salt_id(self, salt_id):
        """Sets the salt_id of this SolutionElement.

        Unique identifier for the node in the SALT model.  # noqa: E501

        :param salt_id: The salt_id of this SolutionElement.
        :type salt_id: str
        """

        self._salt_id = salt_id

    @property
    def sentence_id(self):
        """Gets the sentence_id of this SolutionElement.

        Unique identifier for the sentence in a corpus.  # noqa: E501

        :return: The sentence_id of this SolutionElement.
        :rtype: int
        """
        return self._sentence_id

    @sentence_id.setter
    def sentence_id(self, sentence_id):
        """Sets the sentence_id of this SolutionElement.

        Unique identifier for the sentence in a corpus.  # noqa: E501

        :param sentence_id: The sentence_id of this SolutionElement.
        :type sentence_id: int
        """
        if sentence_id is None:
            raise ValueError("Invalid value for `sentence_id`, must not be `None`")  # noqa: E501

        self._sentence_id = sentence_id

    @property
    def token_id(self):
        """Gets the token_id of this SolutionElement.

        Unique identifier for the token in a sentence.  # noqa: E501

        :return: The token_id of this SolutionElement.
        :rtype: int
        """
        return self._token_id

    @token_id.setter
    def token_id(self, token_id):
        """Sets the token_id of this SolutionElement.

        Unique identifier for the token in a sentence.  # noqa: E501

        :param token_id: The token_id of this SolutionElement.
        :type token_id: int
        """
        if token_id is None:
            raise ValueError("Invalid value for `token_id`, must not be `None`")  # noqa: E501

        self._token_id = token_id