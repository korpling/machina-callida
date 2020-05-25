from datetime import datetime
from typing import List, Dict

from flask import Flask
from flask_migrate import stamp, upgrade
import rapidjson as json
from sqlalchemy.exc import OperationalError

from mcserver.app import db
from mcserver.app.models import CitationLevel, ResourceType, TextComplexityMeasure, AnnisResponse, GraphData, \
    TextComplexity
from mcserver.app.services import CorpusService, CustomCorpusService, TextComplexityService
from mcserver.config import Config
from mcserver.models_auto import Corpus, Exercise, UpdateInfo


class DatabaseService:

    @staticmethod
    def check_corpus_list_age(app: Flask) -> None:
        """ Checks whether the corpus list needs to be updated. If yes, it performs the update. """
        app.logger.info("Corpus update started.")
        ui_cts: UpdateInfo = db.session.query(UpdateInfo).filter_by(resource_type=ResourceType.cts_data.name).first()
        db.session.commit()
        if ui_cts is None:
            app.logger.info("UpdateInfo not available!")
            return
        else:
            ui_datetime: datetime = datetime.fromtimestamp(ui_cts.last_modified_time)
            if (datetime.utcnow() - ui_datetime).total_seconds() > Config.INTERVAL_CORPUS_UPDATE:
                CorpusService.update_corpora()
                ui_cts.last_modified_time = datetime.utcnow().timestamp()
                db.session.commit()
                app.logger.info("Corpus update completed.")

    @staticmethod
    def init_db_alembic() -> None:
        """In Docker, the alembic version is not initially written to the database, so we need to set it manually."""
        if not db.engine.dialect.has_table(db.engine, Config.DATABASE_TABLE_ALEMBIC):
            stamp(directory=Config.MIGRATIONS_DIRECTORY)
        upgrade(directory=Config.MIGRATIONS_DIRECTORY)

    @staticmethod
    def init_db_corpus() -> None:
        """Initializes the corpus list if it is not already there and up to date."""
        if db.engine.dialect.has_table(db.engine, Config.DATABASE_TABLE_CORPUS):
            CorpusService.existing_corpora = db.session.query(Corpus).all()
            db.session.commit()
            urn_dict: Dict[str, int] = {v.source_urn: i for i, v in enumerate(CorpusService.existing_corpora)}
            for cc in CustomCorpusService.custom_corpora:
                if cc.corpus.source_urn in urn_dict:
                    existing_corpus: Corpus = CorpusService.existing_corpora[urn_dict[cc.corpus.source_urn]]
                    CorpusService.update_corpus(title_value=cc.corpus.title, urn=cc.corpus.source_urn,
                                                author=cc.corpus.author, corpus_to_update=existing_corpus,
                                                citation_levels=[cc.corpus.citation_level_1, cc.corpus.citation_level_2,
                                                                 cc.corpus.citation_level_3])
                else:
                    citation_levels: List[CitationLevel] = []
                    for cl in [cc.corpus.citation_level_1, cc.corpus.citation_level_2, cc.corpus.citation_level_3]:
                        citation_levels += [cl] if cl != CitationLevel.default else []
                    CorpusService.add_corpus(title_value=cc.corpus.title, urn=cc.corpus.source_urn,
                                             group_name_value=cc.corpus.author,
                                             citation_levels=citation_levels)
            CorpusService.existing_corpora = db.session.query(Corpus).all()
            db.session.commit()

    @staticmethod
    def init_db_update_info() -> None:
        """Initializes update entries for all resources that have not yet been created."""
        if db.engine.dialect.has_table(db.engine, Config.DATABASE_TABLE_UPDATEINFO):
            for rt in ResourceType:
                ui_cts: UpdateInfo = db.session.query(UpdateInfo).filter_by(resource_type=rt.name).first()
                if ui_cts is None:
                    ui_cts = UpdateInfo.from_dict(resource_type=rt.name, last_modified_time=1,
                                                  created_time=datetime.utcnow().timestamp())
                    db.session.add(ui_cts)
                    db.session.commit()

    @staticmethod
    def init_updater(app: Flask) -> None:
        """Initializes a thread that regularly performs updates."""
        app.app_context().push()
        while True:
            try:
                DatabaseService.check_corpus_list_age(app)
            except OperationalError:
                pass
            import gc
            gc.collect()
            from time import sleep
            # sleep for 1 hour
            sleep(Config.INTERVAL_CORPUS_AGE_CHECK)

    @staticmethod
    def update_exercises(is_csm: bool) -> None:
        """Deletes old exercises."""
        if db.engine.dialect.has_table(db.engine, Config.DATABASE_TABLE_EXERCISE):
            exercises: List[Exercise] = db.session.query(Exercise).all()
            now: datetime = datetime.utcnow()
            for exercise in exercises:
                exercise_datetime: datetime = datetime.fromtimestamp(exercise.last_access_time)
                # delete exercises that have not been accessed for a while, are not compatible anymore, or contain
                # corrupted / empty data
                if (now - exercise_datetime).total_seconds() > Config.INTERVAL_EXERCISE_DELETE or \
                        not exercise.urn or not json.loads(exercise.solutions):
                    db.session.delete(exercise)
                    db.session.commit()
                # manually add text complexity measures for old exercises
                elif not exercise.text_complexity:
                    ar: AnnisResponse = CorpusService.get_corpus(exercise.urn, is_csm=is_csm)
                    tc: TextComplexity = TextComplexityService.text_complexity(TextComplexityMeasure.all.name,
                                                                               exercise.urn, is_csm, ar.graph_data)
                    exercise.text_complexity = tc.all
                    db.session.commit()
