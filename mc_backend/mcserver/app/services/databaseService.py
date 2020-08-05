from datetime import datetime
from typing import Union, Any
from flask_migrate import stamp, upgrade
from sqlalchemy.exc import OperationalError, InvalidRequestError
from sqlalchemy.orm import Query
from mcserver.app import db
from mcserver.app.models import ResourceType
from mcserver.config import Config
from mcserver.models_auto import Corpus, Exercise, UpdateInfo, LearningResult


class DatabaseService:
    @staticmethod
    def commit():
        """Commits the last action to the database and, if it fails, rolls back the current session."""
        try:
            db.session.commit()
        except (OperationalError, InvalidRequestError):
            db.session.rollback()
            raise

    @staticmethod
    def has_table(table: str) -> bool:
        """Checks if a table is present in the database or not."""
        return db.engine.dialect.has_table(db.engine, table)

    @staticmethod
    def init_db_alembic() -> None:
        """In Docker, the alembic version is not initially written to the database, so we need to set it manually."""
        if not DatabaseService.has_table(Config.DATABASE_TABLE_ALEMBIC):
            stamp(directory=Config.MIGRATIONS_DIRECTORY)
        upgrade(directory=Config.MIGRATIONS_DIRECTORY)

    @staticmethod
    def init_db_update_info() -> None:
        """Initializes update entries for all resources that have not yet been created."""
        if DatabaseService.has_table(Config.DATABASE_TABLE_UPDATEINFO):
            for rt in ResourceType:
                ui_cts: UpdateInfo = DatabaseService.query(
                    UpdateInfo, filter_by=dict(resource_type=rt.name), first=True)
                if ui_cts is None:
                    ui_cts = UpdateInfo.from_dict(resource_type=rt.name, last_modified_time=1,
                                                  created_time=datetime.utcnow().timestamp())
                    db.session.add(ui_cts)
                    DatabaseService.commit()

    @staticmethod
    def query(table: Union[Corpus, Exercise, LearningResult, UpdateInfo], filter_by: dict = None,
              first: bool = False) -> Any:
        """Executes a query on the database and rolls back the session if errors occur."""
        try:
            ret_val: Query = db.session.query(table)
            if filter_by:
                ret_val = ret_val.filter_by(**filter_by)
            ret_val = ret_val.first() if first else ret_val.all()
            DatabaseService.commit()
            return ret_val
        except InvalidRequestError:
            db.session.rollback()
            return None
