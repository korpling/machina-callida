# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi.openapi_server.models.base_model_ import Model
from openapi.openapi_server import util


class TextComplexity(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, all=None, avg_w_len=None, avg_w_per_sent=None, lex_den=None, n_abl_abs=None, n_clause=None, n_gerund=None, n_inf=None, n_part=None, n_punct=None, n_sent=None, n_subclause=None, n_types=None, n_w=None, pos=None):  # noqa: E501
        """TextComplexity - a model defined in OpenAPI

        :param all: The all of this TextComplexity.  # noqa: E501
        :type all: float
        :param avg_w_len: The avg_w_len of this TextComplexity.  # noqa: E501
        :type avg_w_len: float
        :param avg_w_per_sent: The avg_w_per_sent of this TextComplexity.  # noqa: E501
        :type avg_w_per_sent: float
        :param lex_den: The lex_den of this TextComplexity.  # noqa: E501
        :type lex_den: float
        :param n_abl_abs: The n_abl_abs of this TextComplexity.  # noqa: E501
        :type n_abl_abs: int
        :param n_clause: The n_clause of this TextComplexity.  # noqa: E501
        :type n_clause: int
        :param n_gerund: The n_gerund of this TextComplexity.  # noqa: E501
        :type n_gerund: int
        :param n_inf: The n_inf of this TextComplexity.  # noqa: E501
        :type n_inf: int
        :param n_part: The n_part of this TextComplexity.  # noqa: E501
        :type n_part: int
        :param n_punct: The n_punct of this TextComplexity.  # noqa: E501
        :type n_punct: int
        :param n_sent: The n_sent of this TextComplexity.  # noqa: E501
        :type n_sent: int
        :param n_subclause: The n_subclause of this TextComplexity.  # noqa: E501
        :type n_subclause: int
        :param n_types: The n_types of this TextComplexity.  # noqa: E501
        :type n_types: int
        :param n_w: The n_w of this TextComplexity.  # noqa: E501
        :type n_w: int
        :param pos: The pos of this TextComplexity.  # noqa: E501
        :type pos: int
        """
        self.openapi_types = {
            'all': float,
            'avg_w_len': float,
            'avg_w_per_sent': float,
            'lex_den': float,
            'n_abl_abs': int,
            'n_clause': int,
            'n_gerund': int,
            'n_inf': int,
            'n_part': int,
            'n_punct': int,
            'n_sent': int,
            'n_subclause': int,
            'n_types': int,
            'n_w': int,
            'pos': int
        }

        self.attribute_map = {
            'all': 'all',
            'avg_w_len': 'avg_w_len',
            'avg_w_per_sent': 'avg_w_per_sent',
            'lex_den': 'lex_den',
            'n_abl_abs': 'n_abl_abs',
            'n_clause': 'n_clause',
            'n_gerund': 'n_gerund',
            'n_inf': 'n_inf',
            'n_part': 'n_part',
            'n_punct': 'n_punct',
            'n_sent': 'n_sent',
            'n_subclause': 'n_subclause',
            'n_types': 'n_types',
            'n_w': 'n_w',
            'pos': 'pos'
        }

        self._all = all
        self._avg_w_len = avg_w_len
        self._avg_w_per_sent = avg_w_per_sent
        self._lex_den = lex_den
        self._n_abl_abs = n_abl_abs
        self._n_clause = n_clause
        self._n_gerund = n_gerund
        self._n_inf = n_inf
        self._n_part = n_part
        self._n_punct = n_punct
        self._n_sent = n_sent
        self._n_subclause = n_subclause
        self._n_types = n_types
        self._n_w = n_w
        self._pos = pos

    @classmethod
    def from_dict(cls, dikt) -> 'TextComplexity':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The TextComplexity of this TextComplexity.  # noqa: E501
        :rtype: TextComplexity
        """
        return util.deserialize_model(dikt, cls)

    @property
    def all(self):
        """Gets the all of this TextComplexity.

        Overall text complexity of the given corpus.  # noqa: E501

        :return: The all of this TextComplexity.
        :rtype: float
        """
        return self._all

    @all.setter
    def all(self, all):
        """Sets the all of this TextComplexity.

        Overall text complexity of the given corpus.  # noqa: E501

        :param all: The all of this TextComplexity.
        :type all: float
        """

        self._all = all

    @property
    def avg_w_len(self):
        """Gets the avg_w_len of this TextComplexity.

        Average length of a word in the given corpus.  # noqa: E501

        :return: The avg_w_len of this TextComplexity.
        :rtype: float
        """
        return self._avg_w_len

    @avg_w_len.setter
    def avg_w_len(self, avg_w_len):
        """Sets the avg_w_len of this TextComplexity.

        Average length of a word in the given corpus.  # noqa: E501

        :param avg_w_len: The avg_w_len of this TextComplexity.
        :type avg_w_len: float
        """

        self._avg_w_len = avg_w_len

    @property
    def avg_w_per_sent(self):
        """Gets the avg_w_per_sent of this TextComplexity.

        Average number of words per sentence.  # noqa: E501

        :return: The avg_w_per_sent of this TextComplexity.
        :rtype: float
        """
        return self._avg_w_per_sent

    @avg_w_per_sent.setter
    def avg_w_per_sent(self, avg_w_per_sent):
        """Sets the avg_w_per_sent of this TextComplexity.

        Average number of words per sentence.  # noqa: E501

        :param avg_w_per_sent: The avg_w_per_sent of this TextComplexity.
        :type avg_w_per_sent: float
        """

        self._avg_w_per_sent = avg_w_per_sent

    @property
    def lex_den(self):
        """Gets the lex_den of this TextComplexity.

        Lexical density of the given corpus.  # noqa: E501

        :return: The lex_den of this TextComplexity.
        :rtype: float
        """
        return self._lex_den

    @lex_den.setter
    def lex_den(self, lex_den):
        """Sets the lex_den of this TextComplexity.

        Lexical density of the given corpus.  # noqa: E501

        :param lex_den: The lex_den of this TextComplexity.
        :type lex_den: float
        """
        if lex_den is not None and lex_den > 1:  # noqa: E501
            raise ValueError("Invalid value for `lex_den`, must be a value less than or equal to `1`")  # noqa: E501
        if lex_den is not None and lex_den < 0:  # noqa: E501
            raise ValueError("Invalid value for `lex_den`, must be a value greater than or equal to `0`")  # noqa: E501

        self._lex_den = lex_den

    @property
    def n_abl_abs(self):
        """Gets the n_abl_abs of this TextComplexity.

        Number of ablativi absoluti in the given corpus.  # noqa: E501

        :return: The n_abl_abs of this TextComplexity.
        :rtype: int
        """
        return self._n_abl_abs

    @n_abl_abs.setter
    def n_abl_abs(self, n_abl_abs):
        """Sets the n_abl_abs of this TextComplexity.

        Number of ablativi absoluti in the given corpus.  # noqa: E501

        :param n_abl_abs: The n_abl_abs of this TextComplexity.
        :type n_abl_abs: int
        """

        self._n_abl_abs = n_abl_abs

    @property
    def n_clause(self):
        """Gets the n_clause of this TextComplexity.

        Number of clauses in the given corpus.  # noqa: E501

        :return: The n_clause of this TextComplexity.
        :rtype: int
        """
        return self._n_clause

    @n_clause.setter
    def n_clause(self, n_clause):
        """Sets the n_clause of this TextComplexity.

        Number of clauses in the given corpus.  # noqa: E501

        :param n_clause: The n_clause of this TextComplexity.
        :type n_clause: int
        """

        self._n_clause = n_clause

    @property
    def n_gerund(self):
        """Gets the n_gerund of this TextComplexity.

        Number of gerunds in the given corpus.  # noqa: E501

        :return: The n_gerund of this TextComplexity.
        :rtype: int
        """
        return self._n_gerund

    @n_gerund.setter
    def n_gerund(self, n_gerund):
        """Sets the n_gerund of this TextComplexity.

        Number of gerunds in the given corpus.  # noqa: E501

        :param n_gerund: The n_gerund of this TextComplexity.
        :type n_gerund: int
        """

        self._n_gerund = n_gerund

    @property
    def n_inf(self):
        """Gets the n_inf of this TextComplexity.

        Number of infinitives in the given corpus.  # noqa: E501

        :return: The n_inf of this TextComplexity.
        :rtype: int
        """
        return self._n_inf

    @n_inf.setter
    def n_inf(self, n_inf):
        """Sets the n_inf of this TextComplexity.

        Number of infinitives in the given corpus.  # noqa: E501

        :param n_inf: The n_inf of this TextComplexity.
        :type n_inf: int
        """

        self._n_inf = n_inf

    @property
    def n_part(self):
        """Gets the n_part of this TextComplexity.

        Number of participles in the given corpus.  # noqa: E501

        :return: The n_part of this TextComplexity.
        :rtype: int
        """
        return self._n_part

    @n_part.setter
    def n_part(self, n_part):
        """Sets the n_part of this TextComplexity.

        Number of participles in the given corpus.  # noqa: E501

        :param n_part: The n_part of this TextComplexity.
        :type n_part: int
        """

        self._n_part = n_part

    @property
    def n_punct(self):
        """Gets the n_punct of this TextComplexity.

        Number of punctuation signs in the given corpus.  # noqa: E501

        :return: The n_punct of this TextComplexity.
        :rtype: int
        """
        return self._n_punct

    @n_punct.setter
    def n_punct(self, n_punct):
        """Sets the n_punct of this TextComplexity.

        Number of punctuation signs in the given corpus.  # noqa: E501

        :param n_punct: The n_punct of this TextComplexity.
        :type n_punct: int
        """

        self._n_punct = n_punct

    @property
    def n_sent(self):
        """Gets the n_sent of this TextComplexity.

        Number of sentences in the given corpus.  # noqa: E501

        :return: The n_sent of this TextComplexity.
        :rtype: int
        """
        return self._n_sent

    @n_sent.setter
    def n_sent(self, n_sent):
        """Sets the n_sent of this TextComplexity.

        Number of sentences in the given corpus.  # noqa: E501

        :param n_sent: The n_sent of this TextComplexity.
        :type n_sent: int
        """

        self._n_sent = n_sent

    @property
    def n_subclause(self):
        """Gets the n_subclause of this TextComplexity.

        Number of subclauses in the given corpus.  # noqa: E501

        :return: The n_subclause of this TextComplexity.
        :rtype: int
        """
        return self._n_subclause

    @n_subclause.setter
    def n_subclause(self, n_subclause):
        """Sets the n_subclause of this TextComplexity.

        Number of subclauses in the given corpus.  # noqa: E501

        :param n_subclause: The n_subclause of this TextComplexity.
        :type n_subclause: int
        """

        self._n_subclause = n_subclause

    @property
    def n_types(self):
        """Gets the n_types of this TextComplexity.

        Number of distinct word forms in the given corpus.  # noqa: E501

        :return: The n_types of this TextComplexity.
        :rtype: int
        """
        return self._n_types

    @n_types.setter
    def n_types(self, n_types):
        """Sets the n_types of this TextComplexity.

        Number of distinct word forms in the given corpus.  # noqa: E501

        :param n_types: The n_types of this TextComplexity.
        :type n_types: int
        """

        self._n_types = n_types

    @property
    def n_w(self):
        """Gets the n_w of this TextComplexity.

        Number of words in the given corpus.  # noqa: E501

        :return: The n_w of this TextComplexity.
        :rtype: int
        """
        return self._n_w

    @n_w.setter
    def n_w(self, n_w):
        """Sets the n_w of this TextComplexity.

        Number of words in the given corpus.  # noqa: E501

        :param n_w: The n_w of this TextComplexity.
        :type n_w: int
        """

        self._n_w = n_w

    @property
    def pos(self):
        """Gets the pos of this TextComplexity.

        Number of distinct part of speech tags in the given corpus.  # noqa: E501

        :return: The pos of this TextComplexity.
        :rtype: int
        """
        return self._pos

    @pos.setter
    def pos(self, pos):
        """Sets the pos of this TextComplexity.

        Number of distinct part of speech tags in the given corpus.  # noqa: E501

        :param pos: The pos of this TextComplexity.
        :type pos: int
        """

        self._pos = pos
