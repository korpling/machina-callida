"""Models for dealing with text data, both in the database and in the application itself."""
from typing import Dict, List, Union, Any
from enum import Enum
import typing
from mcserver.config import Config
from mcserver.models_auto import TExercise, Corpus, TCorpus, Exercise, TLearningResult, LearningResult
from openapi.openapi_server.models import SolutionElement, Solution, Link, NodeMC, TextComplexity, AnnisResponse, \
    GraphData

AnnisResponse = AnnisResponse
GraphData = GraphData
LinkMC = Link
NodeMC = NodeMC
SolutionElement = SolutionElement
TextComplexity = TextComplexity


def make_solution_element_from_salt_id(salt_id: str) -> SolutionElement:
    """Extracts necessary information from a SALT ID string to create a solution element."""
    salt_parts: List[str] = salt_id.split("#")[-1].split("tok")
    sentence_id = int(salt_parts[0].replace("sent", ""))
    token_id = int(salt_parts[1].replace("tok", ""))
    return SolutionElement(content="", salt_id=salt_id, sentence_id=sentence_id, token_id=token_id)


class Case(Enum):
    nominative = 0
    genitive = 1
    dative = 2
    accusative = 3
    ablative = 4
    vocative = 5
    locative = 6


class CitationLevel(Enum):
    """Citation level values for a single corpus."""
    book = "Book"
    chapter = "Chapter"
    default = "default"
    letter = "Letter"
    section = "Section"
    sentence = "Sentence"
    unit = "Unit"


class Dependency(Enum):
    adjectivalClause = 0
    adjectivalModifier = 1
    adverbialClauseModifier = 2
    adverbialModifier = 3
    appositionalModifier = 4
    auxiliary = 5
    caseMarking = 6
    classifier = 7
    clausalComplement = 8
    conjunct = 9
    coordinatingConjunction = 10
    copula = 11
    determiner = 12
    discourseElement = 13
    dislocated = 14
    expletive = 15
    goesWith = 16
    list = 17
    marker = 18
    multiwordExpression = 19
    nominalModifier = 20
    numericModifier = 21
    object = 22
    oblique = 23
    orphan = 24
    parataxis = 25
    punctuation = 26
    root = 27
    subject = 28
    vocative = 29


class ExerciseType(Enum):
    cloze = "ddwtos"
    kwic = "kwic"
    markWords = "markWords"
    matching = "matching"


class FileType(Enum):
    docx = "docx"
    json = "json"
    pdf = "pdf"
    xml = "xml"


class Language(Enum):
    German = "de"
    English = "en"


class Lemma(Enum):
    xxx = "xxx"


class MimeType(Enum):
    docx = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    pdf = "application/pdf"
    xml = "text/xml"


class ObjectType(Enum):
    Activity = "Activity"
    Agent = "Agent"


class PartOfSpeech(Enum):
    adjective = 1
    adverb = 2
    auxiliary = 3
    conjunction = 4
    interjection = 5
    noun = 6
    numeral = 7
    other = 8
    particle = 9
    preposition = 10
    pronoun = 11
    properNoun = 12
    punctuation = 13
    symbol = 14
    verb = 15


class Phenomenon(Enum):
    case = "feats"
    dependency = "dependency"
    lemma = "lemma"
    partOfSpeech = "upostag"


class ResourceType(Enum):
    """Resource types for the UpdateInfo table in the database.

    Each updatable entity has its own resource type value."""
    cts_data = 1
    exercise_list = 2
    file_api_clean = 3


class TextComplexityMeasure(Enum):
    all = 1


class UdPipeInputFormat(Enum):
    tokenize = 1
    conllu = 2
    horizontal = 3


class VocabularyCorpus(Enum):
    agldt = Config.VOCABULARY_AGLDT_FILE_NAME
    bws = Config.VOCABULARY_BWS_FILE_NAME
    proiel = Config.VOCABULARY_PROIEL_FILE_NAME
    viva = Config.VOCABULARY_VIVA_FILE_NAME


class CorpusMC:
    """Keep this synchronized with the implementation in models_auto!

    It is replicated here because the Open-Alchemy package does not correctly assign default values for optional
    parameters."""

    @classmethod
    def from_dict(cls,
                  source_urn: str,
                  author: str = "Anonymus",
                  cid: typing.Optional[int] = None,
                  citation_level_1: str = "default",
                  citation_level_2: str = "default",
                  citation_level_3: str = "default",
                  title: str = "Anonymus",
                  ) -> TCorpus:
        # ignore CID (corpus ID) because it is going to be generated automatically
        return Corpus.from_dict(
            source_urn=source_urn, author=author, citation_level_1=citation_level_1,
            citation_level_2=citation_level_2, citation_level_3=citation_level_3, title=title)


class ExerciseMC:
    """Keep this synchronized with the implementation in models_auto!

    It is replicated here because the Open-Alchemy package does not correctly assign default values for optional
    parameters."""

    @classmethod
    def from_dict(cls,
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
                  ) -> TExercise:
        return Exercise.from_dict(
            eid=eid, last_access_time=last_access_time, correct_feedback=correct_feedback,
            general_feedback=general_feedback, incorrect_feedback=incorrect_feedback,
            instructions=instructions, partially_correct_feedback=partially_correct_feedback,
            search_values=search_values, work_author=work_author, work_title=work_title,
            conll=conll, exercise_type=exercise_type, exercise_type_translation=exercise_type_translation,
            language=language, solutions=solutions, text_complexity=text_complexity, urn=urn)


class LearningResultMC:
    """Keep this synchronized with the implementation in models_auto!

    It is replicated here because the Open-Alchemy package does not correctly assign default values for optional
    parameters."""

    @classmethod
    def from_dict(cls,
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
                  ) -> TLearningResult:
        return LearningResult.from_dict(
            completion=completion, correct_responses_pattern=correct_responses_pattern, created_time=created_time,
            object_definition_description=object_definition_description, response=response, score_max=score_max,
            score_min=score_min, score_raw=score_raw, success=success, actor_account_name=actor_account_name,
            actor_object_type=actor_object_type, category_id=category_id, category_object_type=category_object_type,
            choices=choices, duration=duration, extensions=extensions, interaction_type=interaction_type,
            object_definition_type=object_definition_type, object_object_type=object_object_type,
            score_scaled=score_scaled, verb_display=verb_display, verb_id=verb_id)


class Account:
    def __init__(self, json_dict: dict):
        self.name: str = json_dict["name"]


class Actor:
    def __init__(self, json_dict: dict):
        self.account: Account = Account(json_dict["account"])
        self.object_type: ObjectType = ObjectType(json_dict["objectType"])

    def serialize(self) -> dict:
        return dict(account=self.account.__dict__, objectType=self.object_type.value)


class Category:
    def __init__(self, json_dict: dict):
        self.id: str = json_dict["id"]
        self.object_type: ObjectType = ObjectType(json_dict["objectType"])

    def serialize(self) -> dict:
        return dict(id=self.id, objectType=self.object_type.value)


class Choice:
    def __init__(self, json_dict: dict):
        self.description: Description = Description(json_dict["description"])
        self.id: str = json_dict["id"]

    def serialize(self) -> dict:
        return dict(description={"en-US": self.description.en_us}, id=self.id)


class Description:
    def __init__(self, json_dict: dict):
        self.en_us: str = json_dict["en-US"]


class Display:
    def __init__(self, json_dict: dict):
        self.en_us: str = json_dict["en-US"]


class Verb:
    def __init__(self, json_dict: dict):
        self.id: str = json_dict["id"]
        self.display: Display = Display(json_dict["display"])

    def serialize(self) -> dict:
        return dict(id=self.id, display={"en-US": self.display.en_us})


class Definition:
    def __init__(self, json_dict: dict):
        self.choices: List[Choice] = [Choice(x) for x in json_dict.get("choices", [])]
        self.correct_responses_pattern: List[str] = json_dict["correctResponsesPattern"]
        self.description: Description = Description(json_dict["description"])
        self.extensions: Dict[str, object] = json_dict["extensions"]
        self.interaction_type: str = json_dict["interactionType"]
        self.type: str = json_dict["type"]

    def serialize(self) -> dict:
        return dict(extensions=self.extensions, description=self.description.__dict__, type=self.type,
                    interactionType=self.interaction_type, correctResponsesPattern=self.correct_responses_pattern,
                    choices=[x.serialize() for x in self.choices])


class Object:
    def __init__(self, json_dict: dict):
        self.definition: Definition = Definition(json_dict["definition"])
        self.object_type: ObjectType = ObjectType(json_dict["objectType"])

    def serialize(self) -> dict:
        return dict(objectType=self.object_type.value, definition=self.definition.serialize())


class ContextActivities:
    def __init__(self, json_dict: dict):
        self.category: List[Category] = [Category(x) for x in json_dict["category"]]

    def serialize(self) -> dict:
        return dict(category=[x.serialize() for x in self.category])


class Context:
    def __init__(self, json_dict: dict):
        self.context_activities: ContextActivities = ContextActivities(json_dict["contextActivities"])

    def serialize(self) -> dict:
        return dict(contextActivities=self.context_activities.serialize())


class Score:
    def __init__(self, json_dict: dict):
        self.max: int = json_dict["max"]
        self.min: int = json_dict["min"]
        self.raw: int = json_dict["raw"]
        self.scaled: float = json_dict["scaled"]


class Result:
    def __init__(self, json_dict: dict):
        self.completion: bool = json_dict["completion"]
        self.duration: str = json_dict["duration"]
        self.response: str = json_dict["response"]
        self.score: Score = Score(json_dict["score"])
        self.success: bool = json_dict.get("success", self.score.raw == self.score.max)

    def serialize(self) -> dict:
        return dict(completion=self.completion, success=self.success, duration=self.duration, response=self.response,
                    score=self.score.__dict__)


class XapiStatement:
    def __init__(self, json_dict: dict):
        self.actor: Actor = Actor(json_dict["actor"])
        self.context: Context = Context(json_dict["context"])
        self.object: Object = Object(json_dict["object"])
        self.result: Result = Result(json_dict["result"])
        self.verb: Verb = Verb(json_dict["verb"])

    def serialize(self) -> dict:
        return dict(actor=self.actor.serialize(), verb=self.verb.serialize(), object=self.object.serialize(),
                    context=self.context.serialize(), result=self.result.serialize())


class ExerciseData:
    """Model for exercise data. Holds textual annotations as a graph"""
    graph: GraphData
    solutions: List[Solution]
    uri: str

    def __init__(self, graph: GraphData = None, uri: str = None, solutions: List[Solution] = None,
                 json_dict: dict = None):
        if json_dict is not None:
            self.graph = GraphData.from_dict(json_dict["graph"])
            self.uri = json_dict["uri"]
            self.solutions = [Solution.from_dict(solution_dict) for solution_dict in json_dict["solutions"]]
        else:
            self.graph = graph
            self.solutions = [] if solutions is None else solutions
            self.uri = uri

    def serialize(self) -> dict:
        ret_val: dict = {"solutions": [x.to_dict() for x in self.solutions],
                         "graph": dict(multigraph=self.graph.multigraph, directed=self.graph.directed,
                                       graph=self.graph.graph, nodes=[x.to_dict() for x in self.graph.nodes],
                                       links=[x.to_dict() for x in self.graph.links]), "uri": self.uri}
        return ret_val


class DownloadableFile:
    id: str
    file_name: str
    file_path: str
    file_type: FileType

    def __init__(self, file_id: str, file_name: str, file_type: FileType, file_path: str):
        self.id = file_id
        self.file_type = file_type
        self.file_name = file_name
        self.file_path = file_path


class Citation:
    level: CitationLevel
    label: str
    value: int

    def __init__(self, level: CitationLevel, label: str, value: int):
        self.level = level
        self.label = label
        self.value = value


class BaseTextPart:
    citation: Citation
    text_value: str

    def __init__(self, citation: Citation, text_value: str = ""):
        self.citation = citation
        self.text_value = text_value


class TextPart(BaseTextPart):
    sub_text_parts = None

    def __init__(self, citation: Citation, text_value: str = "", sub_text_parts=None):
        self.sub_text_parts: List[TextPart] = [] if sub_text_parts is None else sub_text_parts
        super().__init__(citation=citation, text_value=text_value)


class CustomCorpus:
    corpus: Corpus
    file_path: str
    text_parts: List[TextPart]

    def __init__(self, corpus: Corpus, file_path: str, text_parts: List[TextPart] = None):
        self.corpus = corpus
        self.file_path = file_path
        self.text_parts: List[TextPart] = [] if text_parts is None else text_parts


class Sentence:
    def __init__(self, id: int, matching_degree: int):
        self.id = id
        self.matching_degree = matching_degree


class StaticExercise:
    def __init__(self, solutions: List[List[str]] = None, urn: str = ""):
        self.solutions = [] if solutions is None else solutions
        self.urn = urn


class FrequencyItem:

    def __init__(self, values: List[str], phenomena: List[Phenomenon], count: Union[int, Any]):
        self.values = values
        self.phenomena = phenomena
        self.count = count

    def serialize(self) -> dict:
        ret_val: dict = self.__dict__
        ret_val["phenomena"] = [x.name for x in self.phenomena]
        return ret_val


class FrequencyAnalysis(List[FrequencyItem]):

    def __init__(self, json_list: list = None):
        if json_list:
            for x in json_list:
                self.append(FrequencyItem(x["values"], [Phenomenon[y] for y in x["phenomena"]], x["count"]))
        else:
            super(FrequencyAnalysis).__init__()

    def serialize(self) -> List[dict]:
        return [x.serialize() for x in self]
