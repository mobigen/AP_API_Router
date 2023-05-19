from fastapi import FastAPI
from sqlalchemy import MetaData
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import declarative_base

from common_service.common.config import settings
from libs.database.tibero import TiberoConnector
from libs.database.orm import SQLAlchemyConnector


# TODO: SQLAlchemy version 수정필요
class SQLAlchemyForCommon(SQLAlchemyConnector):
    def __init__(self, app: FastAPI = None, **kwargs):
        self._table_dict = None
        if app is not None:
            self.init_app(app=app, **kwargs)

        metadata = MetaData()
        for schema in kwargs.get("PG_SCHEMA").split(","):
            metadata.reflect(bind=self.engine, views=True, schema=schema)

        self._Base = automap_base(metadata=metadata)
        self._Base.prepare()

        # self._table_dict = dict(metadata.tables)


Base = declarative_base()
db = SQLAlchemyForCommon(Base) if settings.DB_INFO.type != "tibero" else TiberoConnector()
