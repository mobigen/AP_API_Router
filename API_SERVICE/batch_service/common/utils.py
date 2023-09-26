import re
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI

from batch_service.ELKSearch.Utils.base import set_els
from batch_service.ELKSearch.document import DocumentManager
from batch_service.ELKSearch.index import Index

from libs.database.orm import SQLAlchemyConnector


def default_search_set(server_config, index, size=10, from_=0):
    """
    검색에 필요한 default 세팅
    자동완성과 검색에 사용
    """
    es = set_els(server_config)
    docmanger = DocumentManager(es, index)
    docmanger.set_pagination(size, from_)
    return docmanger


def index_set(server_config):
    es = set_els(server_config)
    return Index(es)


def data_process(row):
    row["re_ctgry"] = re.sub("[ ]", "", str(row["ctgry"]))
    row["re_data_shap"] = re.sub("[ ]", "", str(row["data_shap"]))
    row["re_data_prv_desk"] = re.sub("[ ]", "", str(row["data_prv_desk"]))
    row = default_process(row)
    return row


def default_process(row):
    if "updt_dt" in row.keys() and row["updt_dt"] and len(row["updt_dt"]) > 25:
        if row["updt_dt"][-3:] == "+09":
            row["updt_dt"] = row["updt_dt"][:-3]
        row["updt_dt"] = datetime.strptime(row["updt_dt"], "%Y-%m-%d %H:%M:%S.%f")
    if "reg_date" in row.keys() and row["reg_date"] and len(row["reg_date"]) > 25:
        if row["reg_date"][-3:] == "+09":
            row["reg_date"] = row["reg_date"][:-3]
        row["reg_date"] = datetime.strptime(row["reg_date"], "%Y-%m-%d %H:%M:%S.%f")
    return row


class SeoulOrmConnector(SQLAlchemyConnector):
    def __init__(self, base=None, app: FastAPI = None, **kwargs):
        self._engine = None
        self._Base = base
        self._session = None
        self._metadata = None
        self._schemas = []
        if app is not None:
            self.init_app(app=app, **kwargs)

    def init_app(self, app: FastAPI, **kwargs):
        database_url = kwargs.get("SEOUL_DB_URL")
        pool_recycle = kwargs.get("DB_POOL_RECYCLE", 900)
        is_testing = kwargs.get("TESTING", False)
        echo = kwargs.get("DB_ECHO", False)
        is_reload = kwargs.get("RELOAD", False)
        self._schemas = kwargs.get("SEOUL_DB_INFO").get("SEOUL_SCHEMA").split(",")

        self._engine = create_engine(
            database_url,
            echo=echo,
            pool_recycle=pool_recycle,
            pool_pre_ping=True,
        )
        self._session = sessionmaker(autocommit=False, autoflush=False, bind=self._engine)
        self.reset_metadata()

        @app.on_event("startup")
        def startup():
            self._engine.connect()

        @app.on_event("shutdown")
        def shutdown():
            self._session.close_all()
            self._engine.dispose()
