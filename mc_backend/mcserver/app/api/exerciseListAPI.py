"""The corpus list API. Add it to your REST API to provide users with a list of metadata for available texts."""
from typing import List, Set

import conllu
from conllu import TokenList
from mcserver.app import db
from mcserver.app.models import Language, VocabularyCorpus, ResourceType
from mcserver.app.services import NetworkService, FileService
from mcserver.models_auto import Exercise, UpdateInfo
from openapi.openapi_server.models import MatchingExercise


def get(lang: str, frequency_upper_bound: int, last_update_time: int, vocabulary: str = ""):
    """The GET method for the exercise list REST API. It provides metadata for all available exercises."""
    vocabulary_set: Set[str]
    ui_exercises: UpdateInfo = db.session.query(UpdateInfo).filter_by(
        resource_type=ResourceType.exercise_list.name).first()
    db.session.commit()
    if ui_exercises.last_modified_time < last_update_time / 1000:
        return NetworkService.make_json_response([])
    try:
        vc: VocabularyCorpus = VocabularyCorpus[vocabulary]
        vocabulary_set = FileService.get_vocabulary_set(vc, frequency_upper_bound)
    except KeyError:
        vocabulary_set = set()
    lang: Language
    try:
        lang = Language(lang)
    except ValueError:
        lang = Language.English
    exercises: List[Exercise] = db.session.query(Exercise).filter_by(language=lang.value)
    db.session.commit()
    matching_exercises: List[MatchingExercise] = [MatchingExercise.from_dict(x.to_dict()) for x in exercises]
    if len(vocabulary_set):
        for exercise in matching_exercises:
            conll: List[TokenList] = conllu.parse(exercise.conll)
            lemmata: List[str] = [tok["lemma"] for sent in conll for tok in sent.tokens]
            exercise.matching_degree = sum((1 if x in vocabulary_set else 0) for x in lemmata) / len(lemmata) * 100
    ret_val: List[dict] = [NetworkService.serialize_exercise(x, compress=True) for x in matching_exercises]
    return NetworkService.make_json_response(ret_val)
