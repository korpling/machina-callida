"""Autogenerated SQLAlchemy models based on OpenAlchemy models."""
# pylint: disable=no-member,super-init-not-called,unused-argument

import typing

import sqlalchemy
from sqlalchemy import orm

from open_alchemy import models


class _CorpusDictBase(typing.TypedDict, total=True):
    """TypedDict for properties that are required."""

    source_urn: str


class CorpusDict(_CorpusDictBase, total=False):
    """TypedDict for properties that are not required."""

    author: str
    cid: int
    citation_level_1: str
    citation_level_2: str
    citation_level_3: str
    title: str


class TCorpus(typing.Protocol):
    """
    SQLAlchemy model protocol.

    Collection of texts.

    Attrs:
        author: Author of the texts in the corpus.
        cid: Unique identifier for the corpus.
        citation_level_1: First level for citing the corpus.
        citation_level_2: Second level for citing the corpus.
        citation_level_3: Third level for citing the corpus.
        source_urn: CTS base URN for referencing the corpus.
        title: Corpus title.

    """

    # SQLAlchemy properties
    __table__: sqlalchemy.Table
    __tablename__: str
    query: orm.Query

    # Model properties
    author: str
    cid: int
    citation_level_1: str
    citation_level_2: str
    citation_level_3: str
    source_urn: str
    title: str

    def __init__(
        self,
        source_urn: str,
        author: str = "Anonymus",
        cid: typing.Optional[int] = None,
        citation_level_1: str = "default",
        citation_level_2: str = "default",
        citation_level_3: str = "default",
        title: str = "Anonymus",
    ) -> None:
        """
        Construct.

        Args:
            author: Author of the texts in the corpus.
            cid: Unique identifier for the corpus.
            citation_level_1: First level for citing the corpus.
            citation_level_2: Second level for citing the corpus.
            citation_level_3: Third level for citing the corpus.
            source_urn: CTS base URN for referencing the corpus.
            title: Corpus title.

        """
        ...

    @classmethod
    def from_dict(
        cls,
        source_urn: str,
        author: str = "Anonymus",
        cid: typing.Optional[int] = None,
        citation_level_1: str = "default",
        citation_level_2: str = "default",
        citation_level_3: str = "default",
        title: str = "Anonymus",
    ) -> "TCorpus":
        """
        Construct from a dictionary (eg. a POST payload).

        Args:
            author: Author of the texts in the corpus.
            cid: Unique identifier for the corpus.
            citation_level_1: First level for citing the corpus.
            citation_level_2: Second level for citing the corpus.
            citation_level_3: Third level for citing the corpus.
            source_urn: CTS base URN for referencing the corpus.
            title: Corpus title.

        Returns:
            Model instance based on the dictionary.

        """
        ...

    @classmethod
    def from_str(cls, value: str) -> "TCorpus":
        """
        Construct from a JSON string (eg. a POST payload).

        Returns:
            Model instance based on the JSON string.

        """
        ...

    def to_dict(self) -> CorpusDict:
        """
        Convert to a dictionary (eg. to send back for a GET request).

        Returns:
            Dictionary based on the model instance.

        """
        ...

    def to_str(self) -> str:
        """
        Convert to a JSON string (eg. to send back for a GET request).

        Returns:
            JSON string based on the model instance.

        """
        ...


Corpus: TCorpus = models.Corpus  # type: ignore


class _ExerciseDictBase(typing.TypedDict, total=True):
    """TypedDict for properties that are required."""

    eid: str
    last_access_time: float


class ExerciseDict(_ExerciseDictBase, total=False):
    """TypedDict for properties that are not required."""

    correct_feedback: str
    general_feedback: str
    incorrect_feedback: str
    instructions: str
    partially_correct_feedback: str
    search_values: str
    work_author: str
    work_title: str
    conll: str
    exercise_type: str
    exercise_type_translation: str
    language: str
    solutions: str
    text_complexity: float
    urn: str


class TExercise(typing.Protocol):
    """
    SQLAlchemy model protocol.

    Data for creating and evaluating interactive exercises.

    Attrs:
        correct_feedback: Feedback for successful completion of the exercise.
        general_feedback: Feedback for finishing the exercise.
        incorrect_feedback: Feedback for failing to complete the exercise
            successfully.
        instructions: Hints for how to complete the exercise.
        partially_correct_feedback: Feedback for successfully completing
            certain parts of the exercise.
        search_values: Search queries that were used to build the exercise.
        work_author: Name of the person who wrote the base text for the
            exercise.
        work_title: Title of the base text for the exercise.
        conll: CONLL-formatted linguistic annotations represented as a single
            string.
        eid: Unique identifier (UUID) for the exercise.
        exercise_type: Type of exercise, concerning interaction and layout.
        exercise_type_translation: Localized expression of the exercise type.
        language: ISO 639-1 Language Code for the localization of exercise
            content.
        last_access_time: When the exercise was last accessed (as POSIX
            timestamp).
        solutions: Correct solutions for the exercise.
        text_complexity: Overall text complexity as measured by the software's
            internal language analysis.
        urn: CTS URN for the text passage from which the exercise was created.

    """

    # SQLAlchemy properties
    __table__: sqlalchemy.Table
    __tablename__: str
    query: orm.Query

    # Model properties
    correct_feedback: str
    general_feedback: str
    incorrect_feedback: str
    instructions: str
    partially_correct_feedback: str
    search_values: str
    work_author: str
    work_title: str
    conll: str
    eid: str
    exercise_type: str
    exercise_type_translation: str
    language: str
    last_access_time: float
    solutions: str
    text_complexity: float
    urn: str

    def __init__(
        self,
        eid: str,
        last_access_time: float,
        correct_feedback: str = "",
        general_feedback: str = "",
        incorrect_feedback: str = "",
        instructions: str = "",
        partially_correct_feedback: str = "",
        search_values: str = "[]",
        work_author: str = "",
        work_title: str = "",
        conll: str = "",
        exercise_type: str = "",
        exercise_type_translation: str = "",
        language: str = "de",
        solutions: str = "[]",
        text_complexity: float = 0,
        urn: str = "",
    ) -> None:
        """
        Construct.

        Args:
            correct_feedback: Feedback for successful completion of the
                exercise.
            general_feedback: Feedback for finishing the exercise.
            incorrect_feedback: Feedback for failing to complete the exercise
                successfully.
            instructions: Hints for how to complete the exercise.
            partially_correct_feedback: Feedback for successfully completing
                certain parts of the exercise.
            search_values: Search queries that were used to build the exercise.
            work_author: Name of the person who wrote the base text for the
                exercise.
            work_title: Title of the base text for the exercise.
            conll: CONLL-formatted linguistic annotations represented as a
                single string.
            eid: Unique identifier (UUID) for the exercise.
            exercise_type: Type of exercise, concerning interaction and layout.
            exercise_type_translation: Localized expression of the exercise
                type.
            language: ISO 639-1 Language Code for the localization of exercise
                content.
            last_access_time: When the exercise was last accessed (as POSIX
                timestamp).
            solutions: Correct solutions for the exercise.
            text_complexity: Overall text complexity as measured by the
                software's internal language analysis.
            urn: CTS URN for the text passage from which the exercise was
                created.

        """
        ...

    @classmethod
    def from_dict(
        cls,
        eid: str,
        last_access_time: float,
        correct_feedback: str = "",
        general_feedback: str = "",
        incorrect_feedback: str = "",
        instructions: str = "",
        partially_correct_feedback: str = "",
        search_values: str = "[]",
        work_author: str = "",
        work_title: str = "",
        conll: str = "",
        exercise_type: str = "",
        exercise_type_translation: str = "",
        language: str = "de",
        solutions: str = "[]",
        text_complexity: float = 0,
        urn: str = "",
    ) -> "TExercise":
        """
        Construct from a dictionary (eg. a POST payload).

        Args:
            correct_feedback: Feedback for successful completion of the
                exercise.
            general_feedback: Feedback for finishing the exercise.
            incorrect_feedback: Feedback for failing to complete the exercise
                successfully.
            instructions: Hints for how to complete the exercise.
            partially_correct_feedback: Feedback for successfully completing
                certain parts of the exercise.
            search_values: Search queries that were used to build the exercise.
            work_author: Name of the person who wrote the base text for the
                exercise.
            work_title: Title of the base text for the exercise.
            conll: CONLL-formatted linguistic annotations represented as a
                single string.
            eid: Unique identifier (UUID) for the exercise.
            exercise_type: Type of exercise, concerning interaction and layout.
            exercise_type_translation: Localized expression of the exercise
                type.
            language: ISO 639-1 Language Code for the localization of exercise
                content.
            last_access_time: When the exercise was last accessed (as POSIX
                timestamp).
            solutions: Correct solutions for the exercise.
            text_complexity: Overall text complexity as measured by the
                software's internal language analysis.
            urn: CTS URN for the text passage from which the exercise was
                created.

        Returns:
            Model instance based on the dictionary.

        """
        ...

    @classmethod
    def from_str(cls, value: str) -> "TExercise":
        """
        Construct from a JSON string (eg. a POST payload).

        Returns:
            Model instance based on the JSON string.

        """
        ...

    def to_dict(self) -> ExerciseDict:
        """
        Convert to a dictionary (eg. to send back for a GET request).

        Returns:
            Dictionary based on the model instance.

        """
        ...

    def to_str(self) -> str:
        """
        Convert to a JSON string (eg. to send back for a GET request).

        Returns:
            JSON string based on the model instance.

        """
        ...


Exercise: TExercise = models.Exercise  # type: ignore


class _LearningResultDictBase(typing.TypedDict, total=True):
    """TypedDict for properties that are required."""

    completion: bool
    correct_responses_pattern: str
    created_time: float
    object_definition_description: str
    response: str
    score_max: int
    score_min: int
    score_raw: int
    success: bool


class LearningResultDict(_LearningResultDictBase, total=False):
    """TypedDict for properties that are not required."""

    actor_account_name: str
    actor_object_type: str
    category_id: str
    category_object_type: str
    choices: str
    duration: str
    extensions: str
    interaction_type: str
    object_definition_type: str
    object_object_type: str
    score_scaled: float
    verb_display: str
    verb_id: str


class TLearningResult(typing.Protocol):
    """
    SQLAlchemy model protocol.

    Learner data for completed exercises.

    Attrs:
        actor_account_name: H5P user ID, usually unique per device.
        actor_object_type: Describes the kind of object that was recognized as
            actor.
        category_id: Link to the exercise type specification.
        category_object_type: Describes the kind of object that was recognized
            as exercise.
        choices: JSON string containing a list of possible choices, each with
            ID and description.
        completion: Whether the exercise was fully processed or not.
        correct_responses_pattern: JSON string containing a list of possible
            solutions to the exercise, given as patterns of answers.
        created_time: When the learner data was received (POSIX timestamp).
        duration: How many seconds it took a learner to complete the exercise.
        extensions: JSON string containing a mapping of keys and values
            (usually the local content ID, i.e. a versioning mechanism).
        interaction_type: Exercise type.
        object_definition_description: Exercise content, possibly including
            instructions.
        object_definition_type: Type of object definition that is presented to
            the user.
        object_object_type: Type of object that is presented to the user.
        response: Answer provided by the user, possibly as a pattern.
        score_max: Maximum possible score to be achieved in this exercise.
        score_min: Minimum score to be achieved in this exercise.
        score_raw: Score that was actually achieved by the user in this
            exercise.
        score_scaled: Relative score (between 0 and 1) that was actually
            achieved by the user in this exercise.
        success: Whether the exercise was successfully completed or not.
        verb_display: Type of action that was performed by the user.
        verb_id: Link to the type of action that was performed by the user.

    """

    # SQLAlchemy properties
    __table__: sqlalchemy.Table
    __tablename__: str
    query: orm.Query

    # Model properties
    actor_account_name: str
    actor_object_type: str
    category_id: str
    category_object_type: str
    choices: str
    completion: bool
    correct_responses_pattern: str
    created_time: float
    duration: str
    extensions: str
    interaction_type: str
    object_definition_description: str
    object_definition_type: str
    object_object_type: str
    response: str
    score_max: int
    score_min: int
    score_raw: int
    score_scaled: float
    success: bool
    verb_display: str
    verb_id: str

    def __init__(
        self,
        completion: bool,
        correct_responses_pattern: str,
        created_time: float,
        object_definition_description: str,
        response: str,
        score_max: int,
        score_min: int,
        score_raw: int,
        success: bool,
        actor_account_name: str = "",
        actor_object_type: str = "",
        category_id: str = "",
        category_object_type: str = "",
        choices: str = "[]",
        duration: str = "PT0S",
        extensions: str = "{}",
        interaction_type: str = "",
        object_definition_type: str = "",
        object_object_type: str = "",
        score_scaled: float = 0,
        verb_display: str = "",
        verb_id: str = "",
    ) -> None:
        """
        Construct.

        Args:
            actor_account_name: H5P user ID, usually unique per device.
            actor_object_type: Describes the kind of object that was recognized
                as actor.
            category_id: Link to the exercise type specification.
            category_object_type: Describes the kind of object that was
                recognized as exercise.
            choices: JSON string containing a list of possible choices, each
                with ID and description.
            completion: Whether the exercise was fully processed or not.
            correct_responses_pattern: JSON string containing a list of
                possible solutions to the exercise, given as patterns of
                answers.
            created_time: When the learner data was received (POSIX timestamp).
            duration: How many seconds it took a learner to complete the
                exercise.
            extensions: JSON string containing a mapping of keys and values
                (usually the local content ID, i.e. a versioning mechanism).
            interaction_type: Exercise type.
            object_definition_description: Exercise content, possibly including
                instructions.
            object_definition_type: Type of object definition that is presented
                to the user.
            object_object_type: Type of object that is presented to the user.
            response: Answer provided by the user, possibly as a pattern.
            score_max: Maximum possible score to be achieved in this exercise.
            score_min: Minimum score to be achieved in this exercise.
            score_raw: Score that was actually achieved by the user in this
                exercise.
            score_scaled: Relative score (between 0 and 1) that was actually
                achieved by the user in this exercise.
            success: Whether the exercise was successfully completed or not.
            verb_display: Type of action that was performed by the user.
            verb_id: Link to the type of action that was performed by the user.

        """
        ...

    @classmethod
    def from_dict(
        cls,
        completion: bool,
        correct_responses_pattern: str,
        created_time: float,
        object_definition_description: str,
        response: str,
        score_max: int,
        score_min: int,
        score_raw: int,
        success: bool,
        actor_account_name: str = "",
        actor_object_type: str = "",
        category_id: str = "",
        category_object_type: str = "",
        choices: str = "[]",
        duration: str = "PT0S",
        extensions: str = "{}",
        interaction_type: str = "",
        object_definition_type: str = "",
        object_object_type: str = "",
        score_scaled: float = 0,
        verb_display: str = "",
        verb_id: str = "",
    ) -> "TLearningResult":
        """
        Construct from a dictionary (eg. a POST payload).

        Args:
            actor_account_name: H5P user ID, usually unique per device.
            actor_object_type: Describes the kind of object that was recognized
                as actor.
            category_id: Link to the exercise type specification.
            category_object_type: Describes the kind of object that was
                recognized as exercise.
            choices: JSON string containing a list of possible choices, each
                with ID and description.
            completion: Whether the exercise was fully processed or not.
            correct_responses_pattern: JSON string containing a list of
                possible solutions to the exercise, given as patterns of
                answers.
            created_time: When the learner data was received (POSIX timestamp).
            duration: How many seconds it took a learner to complete the
                exercise.
            extensions: JSON string containing a mapping of keys and values
                (usually the local content ID, i.e. a versioning mechanism).
            interaction_type: Exercise type.
            object_definition_description: Exercise content, possibly including
                instructions.
            object_definition_type: Type of object definition that is presented
                to the user.
            object_object_type: Type of object that is presented to the user.
            response: Answer provided by the user, possibly as a pattern.
            score_max: Maximum possible score to be achieved in this exercise.
            score_min: Minimum score to be achieved in this exercise.
            score_raw: Score that was actually achieved by the user in this
                exercise.
            score_scaled: Relative score (between 0 and 1) that was actually
                achieved by the user in this exercise.
            success: Whether the exercise was successfully completed or not.
            verb_display: Type of action that was performed by the user.
            verb_id: Link to the type of action that was performed by the user.

        Returns:
            Model instance based on the dictionary.

        """
        ...

    @classmethod
    def from_str(cls, value: str) -> "TLearningResult":
        """
        Construct from a JSON string (eg. a POST payload).

        Returns:
            Model instance based on the JSON string.

        """
        ...

    def to_dict(self) -> LearningResultDict:
        """
        Convert to a dictionary (eg. to send back for a GET request).

        Returns:
            Dictionary based on the model instance.

        """
        ...

    def to_str(self) -> str:
        """
        Convert to a JSON string (eg. to send back for a GET request).

        Returns:
            JSON string based on the model instance.

        """
        ...


LearningResult: TLearningResult = models.LearningResult  # type: ignore


class UpdateInfoDict(typing.TypedDict, total=True):
    """TypedDict for properties that are required."""

    created_time: float
    last_modified_time: float
    resource_type: str


class TUpdateInfo(typing.Protocol):
    """
    SQLAlchemy model protocol.

    Timestamps for updates of various resources.

    Attrs:
        created_time: When the resource was created (as POSIX timestamp).
        last_modified_time: When the resource was last modified (as POSIX
            timestamp).
        resource_type: Name of the resource for which update timestamps are
            indexed.

    """

    # SQLAlchemy properties
    __table__: sqlalchemy.Table
    __tablename__: str
    query: orm.Query

    # Model properties
    created_time: float
    last_modified_time: float
    resource_type: str

    def __init__(
        self, created_time: float, last_modified_time: float, resource_type: str
    ) -> None:
        """
        Construct.

        Args:
            created_time: When the resource was created (as POSIX timestamp).
            last_modified_time: When the resource was last modified (as POSIX
                timestamp).
            resource_type: Name of the resource for which update timestamps are
                indexed.

        """
        ...

    @classmethod
    def from_dict(
        cls, created_time: float, last_modified_time: float, resource_type: str
    ) -> "TUpdateInfo":
        """
        Construct from a dictionary (eg. a POST payload).

        Args:
            created_time: When the resource was created (as POSIX timestamp).
            last_modified_time: When the resource was last modified (as POSIX
                timestamp).
            resource_type: Name of the resource for which update timestamps are
                indexed.

        Returns:
            Model instance based on the dictionary.

        """
        ...

    @classmethod
    def from_str(cls, value: str) -> "TUpdateInfo":
        """
        Construct from a JSON string (eg. a POST payload).

        Returns:
            Model instance based on the JSON string.

        """
        ...

    def to_dict(self) -> UpdateInfoDict:
        """
        Convert to a dictionary (eg. to send back for a GET request).

        Returns:
            Dictionary based on the model instance.

        """
        ...

    def to_str(self) -> str:
        """
        Convert to a JSON string (eg. to send back for a GET request).

        Returns:
            JSON string based on the model instance.

        """
        ...


UpdateInfo: TUpdateInfo = models.UpdateInfo  # type: ignore
