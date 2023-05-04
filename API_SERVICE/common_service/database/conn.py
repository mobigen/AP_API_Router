from libs import logging
from libs.database.conn import SQLAlchemy

from fastapi import FastAPI
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker


class SQLAlchemyForCommon(SQLAlchemy):
    def __init__(self, app: FastAPI = None, **kwargs):
        self._table_dict = None
        if app is not None:
            self.init_app(app=app, **kwargs)

        metadata = MetaData()
        for schema in kwargs.get("PG_SCHEMA").split(","):
            metadata.reflect(bind=self.engine, views=True, schema=schema)

        self._Base = automap_base(metadata=metadata)
        self._Base.prepare()

        self._table_dict = dict(metadata.tables)


db = SQLAlchemyForCommon()
