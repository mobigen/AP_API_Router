from datetime import datetime
import json
import logging
from typing import Dict, List, Union, Tuple, Optional

import sqlalchemy
from fastapi import FastAPI
from sqlalchemy import Column, MetaData, and_, create_engine, not_, or_, Table
from sqlalchemy.orm import sessionmaker, Session, Query
from sqlalchemy.sql import column

from .connector import Connector, Executor


logger = logging.getLogger()


class TableNotFoundException(Exception):
    ...


class SQLAlchemyConnector(Connector):
    def __init__(self, base=None, app: FastAPI = None, **kwargs):
        self._engine = None
        self._Base = base
        self._session = None
        self._metadata = None
        self._schemas = []
        if app is not None:
            self.init_app(app=app, **kwargs)

    def init_app(self, app: FastAPI, **kwargs):
        database_url = kwargs.get("DB_URL")
        pool_recycle = kwargs.get("DB_POOL_RECYCLE", 900)
        is_testing = kwargs.get("TESTING", False)
        echo = kwargs.get("DB_ECHO", False)
        is_reload = kwargs.get("RELOAD", False)
        self._schemas = kwargs.get("DB_INFO").get("SCHEMA").split(",")

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

    def get_db(self) -> Executor:
        if self._session is None:
            raise Exception("must be called 'init_db'")
        executor = OrmExecutor(self._session(), self._metadata, self)
        try:
            yield executor
        finally:
            executor.close()

    def reset_metadata(self):
        self._metadata = MetaData()
        for schema in self._schemas:
            self._metadata.reflect(bind=self._engine, views=True, schema=schema)


class OrmExecutor(Executor):
    def __init__(self, session: Session, metadata: MetaData, conn: SQLAlchemyConnector):
        self._session = session
        self._metadata = metadata
        self._conn = conn
        self._cnt = 0
        self._q: Optional[Query] = None

    def query(self, **kwargs) -> "OrmExecutor":
        base_table = self.get_table(kwargs["table_nm"])
        logger.info(base_table)
        key = kwargs.get("key")
        # Join
        if join_info := kwargs.get("join_info"):
            join_table = self.get_table(join_info["table_nm"])
            query = self._session.query(base_table, join_table).join(
                join_table,
                getattr(base_table.columns, key) == getattr(join_table.columns, join_info["key"]),
            )
        else:
            query = self._session.query(base_table)

        # Where
        if where_info := kwargs.get("where_info"):
            filter_val = None
            for where_condition in where_info:
                filter_condition = self._parse_operand(
                    getattr(base_table.columns, where_condition["key"]),
                    where_condition["value"],
                    where_condition["compare_op"],
                )
                if sub_conditions := where_condition.get("sub"):
                    for sub_condition in sub_conditions:
                        sub_filter_condition = self._parse_operand(
                            getattr(base_table.columns, sub_condition["key"]),
                            sub_condition["value"],
                            sub_condition["compare_op"],
                        )
                        # or_ , | 사용무관
                        if sub_condition["op"].lower() == "or":
                            filter_condition = or_(filter_condition, sub_filter_condition)
                        elif sub_condition["op"].lower() == "and":
                            filter_condition = and_(filter_condition, sub_filter_condition)

                if filter_val is not None:
                    if where_condition["op"].lower() == "or":
                        filter_val = filter_val | filter_condition
                    elif where_condition["op"].lower() == "and":
                        filter_val = filter_val & filter_condition
                else:
                    filter_val = filter_condition
            query = query.filter(filter_val)

        self._cnt = query.count()

        # Order
        if order_info := kwargs.get("order_info"):
            order_key = getattr(base_table.columns, order_info["key"])
            query = query.order_by(getattr(sqlalchemy, order_info["order"].lower())(order_key))

        # Paging
        if page_info := kwargs.get("page_info"):
            per_page = page_info["per_page"]
            cur_page = page_info["cur_page"]
            query = query.limit(per_page).offset((cur_page - 1) * per_page)

        self._q = query
        return self

    def all(self) -> Tuple[List[dict], int]:
        columns = self.get_query_columns()
        data = [dict(zip(columns, data)) for data in self._q.all()]

        return json.loads(json.dumps(data, default=str)), self._cnt

    def first(self):
        try:
            columns = self.get_query_columns()
            dat = self._q.first()
            return json.loads(json.dumps(dict(zip(columns, dat)), default=str)) if dat else None
        except Exception as e:
            raise e

    def execute(self, **kwargs):
        try:
            method = kwargs["method"].lower()
            table = self.get_table(kwargs["table_nm"])
            data = self._data_parse(kwargs["data"])

            cond = []
            if keys := kwargs.get("key", []):
                cond = [getattr(table.columns, k) == data[k] for k in keys]

            if method == "insert":
                stmt = table.insert().values(**data)
            elif method == "update":
                stmt = table.update().where(*cond).values(**data)
            elif method == "delete":
                stmt = table.delete().where(*cond)
            else:
                raise NotImplementedError

            self._session.execute(stmt)

            if auto_commit := kwargs.get("auto_commit", True):
                self._session.commit()
        except Exception as e:
            self._session.rollback()
            raise e

    def commit(self):
        self._session.commit()

    def rollback(self):
        self._session.rollback()

    def get_table(self, table_nm) -> Table:
        def __search(table_nm):
            table_nm = table_nm.lower()
            for nm, t in self._metadata.tables.items():
                if nm.lower().endswith(table_nm):
                    return t

        for _ in range(2):
            ret = __search(table_nm)
            if ret is not None:
                return ret
            self._conn.reset_metadata()

        err_msg = f"table not found :: {table_nm}"
        logger.error(f"{err_msg}, {self._metadata.tables.keys()}, {self._conn._schemas}")
        raise TableNotFoundException(err_msg)

    def get_query_columns(self):
        return [desc["name"] for desc in self._q.column_descriptions] if self._q else None

    def _parse_operand(self, key: Column, value: Union[str, int], compare: str):
        compare = compare.lower()
        if compare in ["equal", "="]:
            return key == value
        elif compare in ["not equal", "!="]:
            return key != value
        elif compare in ["greater than", ">"]:
            return key > value
        elif compare in ["greater than or equal", ">="]:
            return key >= value
        elif compare in ["less than", "<"]:
            return key < value
        elif compare in ["less than or equal", "<="]:
            return key <= value
        elif compare == "like":
            return key.like(value)
        elif compare == "not like":
            return not_(key.like(value))
        elif compare == "in":
            return key.in_(value.split(","))
        elif compare == "not in":
            return not_(key.in_(value.split(",")))
        elif compare == "ilike":
            return key.ilike(value)
        else:
            return

    def get_column_info(self, table_nm, schema=None) -> List[Dict[str, str]]:
        ...

    def close(self):
        self._session.close()

    def _data_parse(self, data):
        ret = {}
        for k, v in data.items():
            if str(v).startswith("`"):
                if "+" in v:
                    v = v[1:].split("+")
                    ret[k] = column(v[0].strip()) + int(v[1])
                elif "-" in v:
                    v = v[1:].split("-")
                    data[k] = column(v[0].strip()) - int(v[1])
            elif str(v).upper().startswith("NOW"):
                ret[k] = datetime.now()
            else:
                ret[k] = v
        return ret
