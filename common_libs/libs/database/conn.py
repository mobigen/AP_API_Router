import abc

from fastapi import FastAPI
from sqlalchemy import MetaData, create_engine, inspect
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.common.config import settings


class Connector(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def init_app(self, app: FastAPI, **kwargs):
        ...

    @abc.abstractmethod
    def get_db(self):
        ...

    @abc.abstractmethod
    def select(self, tablename, **kwargs):
        ...

    @abc.abstractmethod
    def execute(self, tablename, **kwargs):
        ...


class SQLAlchemy(Connector):
    def __init__(self, base, app: FastAPI = None, **kwargs):
        self._engine = None
        self._Base = base
        self._session = None
        self._session_instance = None
        self._metadata = None
        self._q = None
        if app is not None:
            self.init_app(app=app, **kwargs)

    def init_app(self, app: FastAPI, **kwargs):
        database_url = kwargs.get("DB_URL")
        pool_recycle = kwargs.get("DB_POOL_RECYCLE", 900)
        is_testing = kwargs.get("TESTING", False)
        echo = kwargs.get("DB_ECHO", True)
        is_reload = kwargs.get("RELOAD", False)

        self._engine = create_engine(
            database_url,
            echo=echo,
            pool_recycle=pool_recycle,
            pool_pre_ping=True,
        )

        self._session = sessionmaker(autocommit=False, autoflush=False, bind=self._engine)

        self._metadata = MetaData()
        for schema in kwargs.get("DB_INFO").get("SCHEMA").split(","):
            self._metadata.reflect(bind=self.engine, views=True, schema=schema)

        @app.on_event("startup")
        def startup():
            self._engine.connect()

        @app.on_event("shutdown")
        def shutdown():
            self._session.close_all()
            self._engine.dispose()

    def get_db(self):
        if self.session is None:
            raise Exception("must be called 'init_db'")
        try:
            self._session_instance = self._session()
            yield self
        finally:
            self._session_instance.close()

    def select(self, tablename, **kwargs):
        cond = []
        table_ = None
        for key, val in kwargs.items():
            key = key.split("__")
            print(f"key :: {key}, v :: {val}")
            if len(key) > 2:
                raise Exception("No 2 more dunders")
            col = getattr(table_.columns, key[0])
            if len(key) == 1:
                cond.append((col == val))
            elif len(key) == 2 and key[1] == "gt":
                cond.append((col > val))
            elif len(key) == 2 and key[1] == "gte":
                cond.append((col >= val))
            elif len(key) == 2 and key[1] == "lt":
                cond.append((col < val))
            elif len(key) == 2 and key[1] == "lte":
                cond.append((col <= val))
            elif len(key) == 2 and key[1] == "in":
                cond.append((col.in_(val)))

        self._q = self._session_instance.query(table_).filter(*cond)

        return self

    def first(self):
        data = self._q.first()
        return data

    def execute(self, **kwargs):
        ...

    @property
    def session(self):
        return self.get_db

    @property
    def engine(self):
        return self._engine

    @property
    def Base(self):
        return self._Base


class TiberoConnector(Connector):
    def __init__(self, **kwargs):
        self.conn = None
        self.cur = None
        self.init_app(kwargs)

    def init_app(self, app: FastAPI, **kwargs):
        import pyodbc

        self.conn = pyodbc.connect(f"DSN={kwargs.get('BASE')};UID={kwargs.get('USER')};PWD={kwargs.get('PASS')}")
        self.conn.setdecoding(pyodbc.SQL_CHAR, encoding="utf-8")
        self.conn.setdecoding(pyodbc.SQL_WCHAR, encoding="utf-8")
        self.conn.setencoding(encoding="utf-8")

    def select(self, **kwargs):
        tablename = kwargs.get("tablename")
        route_url = kwargs.get("route_url")
        method = kwargs.get("method")
        query = f"select * from {tablename} where route_url = '{route_url}' and method = '{method}'"

        try:
            self.cur.execute(query)
            return ([desc[0] for desc in self.cur.description], self.cur.fetchall())
        except Exception as e:
            raise e

    def execute(self, **kwargs):
        ...

    def get_db(self):
        self.cur = self.conn.cursor()
        try:
            yield self
        finally:
            if self.cur:
                self.cur.close()


Base = declarative_base()
db = SQLAlchemy(Base) if settings.DB_INFO.type != "tibero" else TiberoConnector()
