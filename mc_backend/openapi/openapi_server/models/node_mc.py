# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi.openapi_server.models.base_model_ import Model
from openapi.openapi_server import util


class NodeMC(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, annis_node_name=None, annis_node_type=None, annis_tok=None, annis_type=None, id=None, is_oov=None, udep_lemma=None, udep_upostag=None, udep_xpostag=None, udep_feats=None, solution=None):  # noqa: E501
        """NodeMC - a model defined in OpenAPI

        :param annis_node_name: The annis_node_name of this NodeMC.  # noqa: E501
        :type annis_node_name: str
        :param annis_node_type: The annis_node_type of this NodeMC.  # noqa: E501
        :type annis_node_type: str
        :param annis_tok: The annis_tok of this NodeMC.  # noqa: E501
        :type annis_tok: str
        :param annis_type: The annis_type of this NodeMC.  # noqa: E501
        :type annis_type: str
        :param id: The id of this NodeMC.  # noqa: E501
        :type id: str
        :param is_oov: The is_oov of this NodeMC.  # noqa: E501
        :type is_oov: bool
        :param udep_lemma: The udep_lemma of this NodeMC.  # noqa: E501
        :type udep_lemma: str
        :param udep_upostag: The udep_upostag of this NodeMC.  # noqa: E501
        :type udep_upostag: str
        :param udep_xpostag: The udep_xpostag of this NodeMC.  # noqa: E501
        :type udep_xpostag: str
        :param udep_feats: The udep_feats of this NodeMC.  # noqa: E501
        :type udep_feats: str
        :param solution: The solution of this NodeMC.  # noqa: E501
        :type solution: str
        """
        self.openapi_types = {
            'annis_node_name': str,
            'annis_node_type': str,
            'annis_tok': str,
            'annis_type': str,
            'id': str,
            'is_oov': bool,
            'udep_lemma': str,
            'udep_upostag': str,
            'udep_xpostag': str,
            'udep_feats': str,
            'solution': str
        }

        self.attribute_map = {
            'annis_node_name': 'annis_node_name',
            'annis_node_type': 'annis_node_type',
            'annis_tok': 'annis_tok',
            'annis_type': 'annis_type',
            'id': 'id',
            'is_oov': 'is_oov',
            'udep_lemma': 'udep_lemma',
            'udep_upostag': 'udep_upostag',
            'udep_xpostag': 'udep_xpostag',
            'udep_feats': 'udep_feats',
            'solution': 'solution'
        }

        self._annis_node_name = annis_node_name
        self._annis_node_type = annis_node_type
        self._annis_tok = annis_tok
        self._annis_type = annis_type
        self._id = id
        self._is_oov = is_oov
        self._udep_lemma = udep_lemma
        self._udep_upostag = udep_upostag
        self._udep_xpostag = udep_xpostag
        self._udep_feats = udep_feats
        self._solution = solution

    @classmethod
    def from_dict(cls, dikt) -> 'NodeMC':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The NodeMC of this NodeMC.  # noqa: E501
        :rtype: NodeMC
        """
        return util.deserialize_model(dikt, cls)

    @property
    def annis_node_name(self):
        """Gets the annis_node_name of this NodeMC.

        Node name as given by ANNIS.  # noqa: E501

        :return: The annis_node_name of this NodeMC.
        :rtype: str
        """
        return self._annis_node_name

    @annis_node_name.setter
    def annis_node_name(self, annis_node_name):
        """Sets the annis_node_name of this NodeMC.

        Node name as given by ANNIS.  # noqa: E501

        :param annis_node_name: The annis_node_name of this NodeMC.
        :type annis_node_name: str
        """

        self._annis_node_name = annis_node_name

    @property
    def annis_node_type(self):
        """Gets the annis_node_type of this NodeMC.

        Node type as given by ANNIS.  # noqa: E501

        :return: The annis_node_type of this NodeMC.
        :rtype: str
        """
        return self._annis_node_type

    @annis_node_type.setter
    def annis_node_type(self, annis_node_type):
        """Sets the annis_node_type of this NodeMC.

        Node type as given by ANNIS.  # noqa: E501

        :param annis_node_type: The annis_node_type of this NodeMC.
        :type annis_node_type: str
        """

        self._annis_node_type = annis_node_type

    @property
    def annis_tok(self):
        """Gets the annis_tok of this NodeMC.

        Raw word form as given by ANNIS.  # noqa: E501

        :return: The annis_tok of this NodeMC.
        :rtype: str
        """
        return self._annis_tok

    @annis_tok.setter
    def annis_tok(self, annis_tok):
        """Sets the annis_tok of this NodeMC.

        Raw word form as given by ANNIS.  # noqa: E501

        :param annis_tok: The annis_tok of this NodeMC.
        :type annis_tok: str
        """

        self._annis_tok = annis_tok

    @property
    def annis_type(self):
        """Gets the annis_type of this NodeMC.

        Node type as given by ANNIS (?).  # noqa: E501

        :return: The annis_type of this NodeMC.
        :rtype: str
        """
        return self._annis_type

    @annis_type.setter
    def annis_type(self, annis_type):
        """Sets the annis_type of this NodeMC.

        Node type as given by ANNIS (?).  # noqa: E501

        :param annis_type: The annis_type of this NodeMC.
        :type annis_type: str
        """

        self._annis_type = annis_type

    @property
    def id(self):
        """Gets the id of this NodeMC.

        Unique identifier for the node in the SALT model.  # noqa: E501

        :return: The id of this NodeMC.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this NodeMC.

        Unique identifier for the node in the SALT model.  # noqa: E501

        :param id: The id of this NodeMC.
        :type id: str
        """

        self._id = id

    @property
    def is_oov(self):
        """Gets the is_oov of this NodeMC.

        Whether the raw word form is missing in a given vocabulary.  # noqa: E501

        :return: The is_oov of this NodeMC.
        :rtype: bool
        """
        return self._is_oov

    @is_oov.setter
    def is_oov(self, is_oov):
        """Sets the is_oov of this NodeMC.

        Whether the raw word form is missing in a given vocabulary.  # noqa: E501

        :param is_oov: The is_oov of this NodeMC.
        :type is_oov: bool
        """

        self._is_oov = is_oov

    @property
    def udep_lemma(self):
        """Gets the udep_lemma of this NodeMC.

        Lemmatized word form.  # noqa: E501

        :return: The udep_lemma of this NodeMC.
        :rtype: str
        """
        return self._udep_lemma

    @udep_lemma.setter
    def udep_lemma(self, udep_lemma):
        """Sets the udep_lemma of this NodeMC.

        Lemmatized word form.  # noqa: E501

        :param udep_lemma: The udep_lemma of this NodeMC.
        :type udep_lemma: str
        """

        self._udep_lemma = udep_lemma

    @property
    def udep_upostag(self):
        """Gets the udep_upostag of this NodeMC.

        Universal part of speech tag for the word form.  # noqa: E501

        :return: The udep_upostag of this NodeMC.
        :rtype: str
        """
        return self._udep_upostag

    @udep_upostag.setter
    def udep_upostag(self, udep_upostag):
        """Sets the udep_upostag of this NodeMC.

        Universal part of speech tag for the word form.  # noqa: E501

        :param udep_upostag: The udep_upostag of this NodeMC.
        :type udep_upostag: str
        """

        self._udep_upostag = udep_upostag

    @property
    def udep_xpostag(self):
        """Gets the udep_xpostag of this NodeMC.

        Language-specific part of speech tag for the word form.  # noqa: E501

        :return: The udep_xpostag of this NodeMC.
        :rtype: str
        """
        return self._udep_xpostag

    @udep_xpostag.setter
    def udep_xpostag(self, udep_xpostag):
        """Sets the udep_xpostag of this NodeMC.

        Language-specific part of speech tag for the word form.  # noqa: E501

        :param udep_xpostag: The udep_xpostag of this NodeMC.
        :type udep_xpostag: str
        """

        self._udep_xpostag = udep_xpostag

    @property
    def udep_feats(self):
        """Gets the udep_feats of this NodeMC.

        Additional morphological information.  # noqa: E501

        :return: The udep_feats of this NodeMC.
        :rtype: str
        """
        return self._udep_feats

    @udep_feats.setter
    def udep_feats(self, udep_feats):
        """Sets the udep_feats of this NodeMC.

        Additional morphological information.  # noqa: E501

        :param udep_feats: The udep_feats of this NodeMC.
        :type udep_feats: str
        """

        self._udep_feats = udep_feats

    @property
    def solution(self):
        """Gets the solution of this NodeMC.

        Solution value for this node in an exercise.  # noqa: E501

        :return: The solution of this NodeMC.
        :rtype: str
        """
        return self._solution

    @solution.setter
    def solution(self, solution):
        """Sets the solution of this NodeMC.

        Solution value for this node in an exercise.  # noqa: E501

        :param solution: The solution of this NodeMC.
        :type solution: str
        """

        self._solution = solution
