import logging
from urllib import parse

from fastapi import FastAPI
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from ..common.config import settings


def _database_exist(engine, schema_name):
    query = f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{schema_name}'"
    with engine.connect() as conn:
        result_proxy = conn.execute(query)
        result = result_proxy.scalar()  # return first column of first row
        return bool(result)


def _drop_database(engine, schema_name):
    with engine.connect() as conn:
        conn.execute(f"DROP DATABASE {schema_name};")


def _create_database(engine, schema_name):
    with engine.connect() as conn:
        conn.execute(
            f"CREATE DATABASE {schema_name} WITH OWNER {settings.PG_USER} ENCODING 'utf8'"
        )


class SQLAlchemy:
    def __init__(self, app: FastAPI = None, **kwargs):
        self._engine = None
        self._session = None
        if app is not None:
            self.init_app(app=app, **kwargs)

    def init_app(self, app: FastAPI, **kwargs):
        database_url = (
            "postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}".format(
                user=settings.PG_USER,
                password=parse.quote(settings.PG_PASS.get_secret_value()),
                host=settings.PG_HOST,
                port=settings.PG_PORT,
                dbname=settings.PG_BASE,
            )
        )
        pool_recycle = settings.DB_POOL_RECYCLE
        is_testing = settings.TESTING
        echo = settings.DB_ECHO
        is_reload = settings.RELOAD

        self._engine = create_engine(
            database_url,
            echo=echo,
            pool_recycle=pool_recycle,
            pool_pre_ping=True,
        )

        if is_testing:
            db_url = self._engine.url
            if db_url.host != "localhost":
                print(db_url.host)
                raise Exception("db host must be 'localhost' in test environment")
            except_schema_db_url = f"{db_url.drivername}://{db_url.username}:{db_url.password}@{db_url.host}/{db_url.database}"
            schema_name = db_url.database
            temp_engine = create_engine(
                except_schema_db_url,
                echo=echo,
                pool_recycle=pool_recycle,
                pool_pre_ping=True,
            )
            temp_engine.raw_connection().set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

            if is_reload:
                if _database_exist(temp_engine, schema_name):
                    _drop_database(temp_engine, schema_name)
                _create_database(temp_engine, schema_name)
                temp_engine.dispose()

        self._session = sessionmaker(
            autocommit=False, autoflush=False, bind=self._engine
        )

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


db = SQLAlchemy()
Base = declarative_base()
