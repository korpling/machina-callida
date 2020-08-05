from datetime import datetime
from typing import List, Dict
import rapidjson as json
from mcserver import Config
from mcserver.app import db
from mcserver.app.models import AnnisResponse, TextComplexity, TextComplexityMeasure, GraphData, ExerciseData
from mcserver.app.services import DatabaseService, CorpusService, TextComplexityService, AnnotationService
from mcserver.models_auto import Exercise
from openapi.openapi_server.models import Solution


class ExerciseService:
    """ Service for creating new and managing old exercises. """

    @staticmethod
    def map_graph_data_to_exercise(graph_data_raw: Dict, xml_guid: str, solutions: List[Solution]):
        """ Creates an ExerciseData object from the separate parts. """
        # create the basis for the download URL
        xml_url = "/" + xml_guid
        graph_data: GraphData = AnnotationService.map_graph_data(graph_data_raw)
        return ExerciseData(graph=graph_data, solutions=solutions, uri=xml_url)

    @staticmethod
    def update_exercises(is_csm: bool) -> None:
        """Deletes old exercises."""
        if DatabaseService.has_table(Config.DATABASE_TABLE_EXERCISE):
            exercises: List[Exercise] = DatabaseService.query(Exercise)
            now: datetime = datetime.utcnow()
            for exercise in exercises:
                exercise_datetime: datetime = datetime.fromtimestamp(exercise.last_access_time)
                # delete exercises that have not been accessed for a while, are not compatible anymore, or contain
                # corrupted / empty data
                if (now - exercise_datetime).total_seconds() > Config.INTERVAL_EXERCISE_DELETE or \
                        not exercise.urn or not json.loads(exercise.solutions):
                    db.session.delete(exercise)
                    DatabaseService.commit()
                # manually add text complexity measures for old exercises
                elif not exercise.text_complexity:
                    ar: AnnisResponse = CorpusService.get_corpus(exercise.urn, is_csm=is_csm)
                    tc: TextComplexity = TextComplexityService.text_complexity(
                        TextComplexityMeasure.all.name, exercise.urn, is_csm, ar.graph_data)
                    exercise.text_complexity = tc.all
                    DatabaseService.commit()
