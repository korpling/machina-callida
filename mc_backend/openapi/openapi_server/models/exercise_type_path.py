# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi.openapi_server.models.base_model_ import Model
from openapi.openapi_server import util


class ExerciseTypePath(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    """
    allowed enum values
    """
    DRAG_TEXT = "drag_text"
    FILL_BLANKS = "fill_blanks"
    MARK_WORDS = "mark_words"
    MULTI_CHOICE = "multi_choice"
    VOC_LIST = "voc_list"
    def __init__(self):  # noqa: E501
        """ExerciseTypePath - a model defined in OpenAPI

        """
        self.openapi_types = {
        }

        self.attribute_map = {
        }

    @classmethod
    def from_dict(cls, dikt) -> 'ExerciseTypePath':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The ExerciseTypePath of this ExerciseTypePath.  # noqa: E501
        :rtype: ExerciseTypePath
        """
        return util.deserialize_model(dikt, cls)
