# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi.openapi_server.models.base_model_ import Model
from openapi.openapi_server import util


class Corpus(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, author='Anonymus', cid=None, citation_level_1='default', citation_level_2='default', citation_level_3='default', source_urn=None, title='Anonymus'):  # noqa: E501
        """Corpus - a model defined in OpenAPI

        :param author: The author of this Corpus.  # noqa: E501
        :type author: str
        :param cid: The cid of this Corpus.  # noqa: E501
        :type cid: int
        :param citation_level_1: The citation_level_1 of this Corpus.  # noqa: E501
        :type citation_level_1: str
        :param citation_level_2: The citation_level_2 of this Corpus.  # noqa: E501
        :type citation_level_2: str
        :param citation_level_3: The citation_level_3 of this Corpus.  # noqa: E501
        :type citation_level_3: str
        :param source_urn: The source_urn of this Corpus.  # noqa: E501
        :type source_urn: str
        :param title: The title of this Corpus.  # noqa: E501
        :type title: str
        """
        self.openapi_types = {
            'author': str,
            'cid': int,
            'citation_level_1': str,
            'citation_level_2': str,
            'citation_level_3': str,
            'source_urn': str,
            'title': str
        }

        self.attribute_map = {
            'author': 'author',
            'cid': 'cid',
            'citation_level_1': 'citation_level_1',
            'citation_level_2': 'citation_level_2',
            'citation_level_3': 'citation_level_3',
            'source_urn': 'source_urn',
            'title': 'title'
        }

        self._author = author
        self._cid = cid
        self._citation_level_1 = citation_level_1
        self._citation_level_2 = citation_level_2
        self._citation_level_3 = citation_level_3
        self._source_urn = source_urn
        self._title = title

    @classmethod
    def from_dict(cls, dikt) -> 'Corpus':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Corpus of this Corpus.  # noqa: E501
        :rtype: Corpus
        """
        return util.deserialize_model(dikt, cls)

    @property
    def author(self):
        """Gets the author of this Corpus.

        Author of the texts in the corpus.  # noqa: E501

        :return: The author of this Corpus.
        :rtype: str
        """
        return self._author

    @author.setter
    def author(self, author):
        """Sets the author of this Corpus.

        Author of the texts in the corpus.  # noqa: E501

        :param author: The author of this Corpus.
        :type author: str
        """

        self._author = author

    @property
    def cid(self):
        """Gets the cid of this Corpus.

        Unique identifier for the corpus.  # noqa: E501

        :return: The cid of this Corpus.
        :rtype: int
        """
        return self._cid

    @cid.setter
    def cid(self, cid):
        """Sets the cid of this Corpus.

        Unique identifier for the corpus.  # noqa: E501

        :param cid: The cid of this Corpus.
        :type cid: int
        """

        self._cid = cid

    @property
    def citation_level_1(self):
        """Gets the citation_level_1 of this Corpus.

        First level for citing the corpus.  # noqa: E501

        :return: The citation_level_1 of this Corpus.
        :rtype: str
        """
        return self._citation_level_1

    @citation_level_1.setter
    def citation_level_1(self, citation_level_1):
        """Sets the citation_level_1 of this Corpus.

        First level for citing the corpus.  # noqa: E501

        :param citation_level_1: The citation_level_1 of this Corpus.
        :type citation_level_1: str
        """

        self._citation_level_1 = citation_level_1

    @property
    def citation_level_2(self):
        """Gets the citation_level_2 of this Corpus.

        Second level for citing the corpus.  # noqa: E501

        :return: The citation_level_2 of this Corpus.
        :rtype: str
        """
        return self._citation_level_2

    @citation_level_2.setter
    def citation_level_2(self, citation_level_2):
        """Sets the citation_level_2 of this Corpus.

        Second level for citing the corpus.  # noqa: E501

        :param citation_level_2: The citation_level_2 of this Corpus.
        :type citation_level_2: str
        """

        self._citation_level_2 = citation_level_2

    @property
    def citation_level_3(self):
        """Gets the citation_level_3 of this Corpus.

        Third level for citing the corpus.  # noqa: E501

        :return: The citation_level_3 of this Corpus.
        :rtype: str
        """
        return self._citation_level_3

    @citation_level_3.setter
    def citation_level_3(self, citation_level_3):
        """Sets the citation_level_3 of this Corpus.

        Third level for citing the corpus.  # noqa: E501

        :param citation_level_3: The citation_level_3 of this Corpus.
        :type citation_level_3: str
        """

        self._citation_level_3 = citation_level_3

    @property
    def source_urn(self):
        """Gets the source_urn of this Corpus.

        CTS base URN for referencing the corpus.  # noqa: E501

        :return: The source_urn of this Corpus.
        :rtype: str
        """
        return self._source_urn

    @source_urn.setter
    def source_urn(self, source_urn):
        """Sets the source_urn of this Corpus.

        CTS base URN for referencing the corpus.  # noqa: E501

        :param source_urn: The source_urn of this Corpus.
        :type source_urn: str
        """
        if source_urn is None:
            raise ValueError("Invalid value for `source_urn`, must not be `None`")  # noqa: E501

        self._source_urn = source_urn

    @property
    def title(self):
        """Gets the title of this Corpus.

        Corpus title.  # noqa: E501

        :return: The title of this Corpus.
        :rtype: str
        """
        return self._title

    @title.setter
    def title(self, title):
        """Sets the title of this Corpus.

        Corpus title.  # noqa: E501

        :param title: The title of this Corpus.
        :type title: str
        """

        self._title = title
