import abc
import logging
from typing import Dict, List, Union, Tuple

import pyodbc
import sqlalchemy
from fastapi import FastAPI
from sqlalchemy import Column, MetaData, and_, create_engine, not_, or_
from sqlalchemy.orm import Session, sessionmaker

logger = logging.getLogger()


class Connector(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def init_app(self, app: FastAPI, **kwargs):
        ...

    @abc.abstractmethod
    def get_db(self):
        ...

    @abc.abstractmethod
    def query(self, **kwargs):
        ...

    @abc.abstractmethod
    def all(self):
        ...

    @abc.abstractmethod
    def first(self):
        ...

    @abc.abstractmethod
    def execute(self, tablename, **kwargs):
        ...


class SQLAlchemy(Connector):
    def __init__(self, base=None, app: FastAPI = None, **kwargs):
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

    def get_db(self) -> Session:
        if self.session is None:
            raise Exception("must be called 'init_db'")
        try:
            self._session_instance = self._session()
            yield self
        finally:
            self._session_instance.close()

    def select(self, **kwargs) -> Tuple[List[dict], int]:
        base_table = self.get_table(kwargs["table_nm"])
        key = kwargs["key"]
        # Join
        if join_info := kwargs["join_info"]:
            join_table = self.get_table(join_info.table_nm)
            query = self._session_instance.query(base_table, join_table).join(
                join_table,
                getattr(base_table.columns, key) == getattr(join_table.columns, join_info.key),
            )
        else:
            query = self._session_instance.query(base_table)

        # Where
        if where_info := kwargs["where_info"]:
            filter_val = None
            for where_condition in where_info:
                filter_condition = self._parse_operand(
                    getattr(base_table.columns, where_condition.key),
                    where_condition.value,
                    where_condition.compare_op,
                )
                if sub_conditions := where_condition.sub_conditions:
                    for sub_condition in sub_conditions:
                        sub_filter_condition = self._parse_operand(
                            getattr(base_table.columns, sub_condition.key),
                            sub_condition.value,
                            sub_condition.compare_op,
                        )
                        # or_ , | 사용무관
                        if sub_condition.op.lower() == "or":
                            filter_condition = or_(filter_condition, sub_filter_condition)
                        elif sub_condition.op.lower() == "and":
                            filter_condition = and_(filter_condition, sub_filter_condition)

                if filter_val is not None:
                    if where_condition.op.lower() == "or":
                        filter_val = filter_val | filter_condition
                    elif where_condition.op.lower() == "and":
                        filter_val = filter_val & filter_condition
                else:
                    filter_val = filter_condition
            query = query.filter(filter_val)

        count = query.count()

        # Order
        if order_info := kwargs["order_info"]:
            order_key = getattr(base_table.columns, order_info.key)
            query = query.order_by(getattr(sqlalchemy, order_info.order.lower())(order_key))

        # Paging
        if page_info := kwargs["page_info"]:
            per_page = page_info.per_page
            cur_page = page_info.cur_page
            query = query.limit(per_page).offset((cur_page - 1) * per_page)

        data = [dict(zip([column.name for column in base_table.columns], data)) for data in query.all()]

        return data, count

    def first(self):
        data = self._q.first()
        return data

    def execute(self, **kwargs):
        ...

    def get_table(self, table_nm):
        for nm, t in self._metadata.tables.items():
            if table_nm in nm:
                return t

    def _parse_operand(key: Column, value: Union[str, int], compare: str):
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

    @property
    def session(self):
        if self._session_instance:
            return self._session_instance

    @property
    def engine(self):
        return self._engine

    @property
    def Base(self):
        return self._Base


class TiberoConnector(Connector):
    def __init__(self, app: FastAPI = None, **kwargs):
        self.conn = None
        self.cur = None
        self._q = None
        if app is not None:
            self.init_app(app, kwargs)

    def init_app(self, app: FastAPI, **kwargs):
        self.conn = pyodbc.connect(kwargs.get("DB_URL"))
        self.conn.setdecoding(pyodbc.SQL_CHAR, encoding="utf-8")
        self.conn.setdecoding(pyodbc.SQL_WCHAR, encoding="utf-32le")
        self.conn.setdecoding(pyodbc.SQL_WMETADATA, encoding="utf-32le")
        self.conn.setencoding(encoding="utf-8")

    def query(self, **kwargs):
        table_nm = kwargs.get("table_nm")
        join_key = kwargs.get("key")

        query = f"select * from {table_nm} "
        if join_info := kwargs.get("join_info"):
            t = join_info["table_nm"]
            k = join_info["key"]
            query += f"join {t} on {table_nm}.{join_key} = {t}.{k} "

        if where_info := kwargs.get("where_info"):
            query += f"where "
            for info in where_info:
                t = info["table_nm"]
                k = info["key"]
                val = info["value"]
                compare_op = self._parse_operand(info["compare_op"])
                op = info["op"]
                query += f"{op} {t}.{k} {compare_op} '{val}' "

        if order_info := kwargs.get("order_info"):
            t = order_info["table_nm"]
            k = order_info["key"]
            o = order_info["order"]
            query += f"order by {t}.{k} {str(o).upper()} "

        if page_info := kwargs.get("page_info"):
            p = page_info["per_page"]
            c = page_info["cur_page"]
            query += f"limit {p} offset {c}"

        self._q = query
        logger.info(query)
        return self

    def all(self) -> Tuple[List[dict], int]:
        try:
            data = self.cur.execute(self._q).fetchall()
            if data:
                rows = [dict(zip(self._get_headers(), row)) for row in data]
                return (rows, int(self.cur.execute(self._q.replace("*", "count(*)")).fetchone()[0]))
        except Exception as e:
            raise e

    def first(self) -> Dict:
        try:
            data = self.cur.execute(self._q).fetchone()
            if data:
                return dict(zip(self._get_headers(), data))
        except Exception as e:
            raise e

    def execute(self, **kwargs):
        ...

    def _get_headers(self) -> list[str]:
        return [d[0].lower() for d in self.cur.description]

    def get_db(self) -> pyodbc.Cursor:
        self.cur = self.conn.cursor()
        try:
            yield self
        finally:
            if self.cur:
                self.cur.close()

    def _parse_operand(self, operand):
        if operand == "Equal":
            return "="
        elif operand == "Not Equal":
            return "!="
        elif operand == "Greater Than":
            return ">"
        elif operand == "Greater Than or Equal":
            return ">="
        elif operand == "Less Than":
            return "<"
        elif operand == "Less Than or Equal":
            return "<="
        else:
            return operand

    def get_column_info(self, table_nm):
        # OWNER, TABLE_NAME, COLUMN_NAME, COMMENT
        query = f"SELECT * FROM ALL_COL_COMMENTS WHERE TABLE_NAME = '{table_nm.upper()}';"
        logger.info(query)
        self.cur.execute(query)
        return [{"column_name": row[2], "kor_column_name": row[3]} for row in self.cur.fetchall()]
