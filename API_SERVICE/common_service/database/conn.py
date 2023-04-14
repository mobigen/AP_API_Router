import logging

from fastapi import FastAPI
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


class SQLAlchemy:
    def __init__(self, app: FastAPI = None, **kwargs):
        self._engine = None
        self._session = None
        self._Base = None
        self._table_dict = None
        if app is not None:
            self.init_app(app=app, **kwargs)

    def init_app(self, app: FastAPI, **kwargs):
        database_url = kwargs.get("DB_URL")
        pool_recycle = kwargs.get("DB_POOL_RECYCLE", 900)
        db_echo = kwargs.get("DB_ECHO", True)

        self._engine = create_engine(
            database_url,
            echo=db_echo,
            pool_recycle=pool_recycle,
            pool_pre_ping=True,
        )

        metadata = MetaData()
        for schema in kwargs.get("PG_SCHEMA").split(","):
            metadata.reflect(bind=self._engine, views=True, schema=schema)

        self._Base = automap_base(metadata=metadata)
        self._Base.prepare()

        self._table_dict = dict(metadata.tables)
        print(dir(metadata))
        print(dir(self._Base))
        print(self._Base.classes)
        print(dir(self._Base.classes))

        print(len(self._table_dict))

        self._session = sessionmaker(autocommit=False, autoflush=False, bind=self._engine)

        @app.on_event("startup")
        def startup():
            self._engine.connect()
            logging.info("DB connected.")

        @app.on_event("shutdown")
        def shutdown():
            self._session.close_all()
            self._engine.dispose()
            logging.info("DB disconnected.")

    def get_db(self):
        if self.session is None:
            raise Exception("must be called 'init_db'")
        db_session = None
        try:
            db_session = self._session()
            yield db_session
        finally:
            db_session.close()

    @property
    def session(self):
        return self.get_db

    @property
    def engine(self):
        return self._engine

    def get_table(self, table_nm):
        for nm, t in self._table_dict.items():
            if table_nm in nm:
                return t


db = SQLAlchemy()
# Base = declarative_base()
