import abc
import logging
from typing import Dict, List, Union, Tuple, TypeVar

import pyodbc
import sqlalchemy
from fastapi import FastAPI
from sqlalchemy import Column, MetaData, and_, create_engine, not_, or_
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger()


T = TypeVar('T', bound="Connector")


class Connector(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def init_app(self, app: FastAPI, **kwargs):
        ...

    @abc.abstractmethod
    def get_db(self) -> T:
        ...

    @abc.abstractmethod
    def query(self, **kwargs) -> T:
        ...

    @abc.abstractmethod
    def all(self) -> Tuple[List[dict], int]:
        ...

    @abc.abstractmethod
    def first(self) -> dict:
        ...

    @abc.abstractmethod
    def execute(self, tablename, **kwargs):
        ...

    @abc.abstractmethod
    def get_column_info(self, table_nm) -> List[Dict[str, str]]:
        ...


class SQLAlchemyConnector(Connector):
    # TODO: 임시작성 추후에 실 사용시 수정필요
    def __init__(self, base=None, app: FastAPI = None, **kwargs):
        self._engine = None
        self._Base = base
        self._session = None
        self._session_instance = None
        self._metadata = None
        self._q = None
        self._cnt = 0
        self._column_names = []
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

    def get_db(self) -> "SQLAlchemyConnector":
        if self.session is None:
            raise Exception("must be called 'init_db'")
        try:
            self._session_instance = self._session()
            yield self
        finally:
            self._session_instance.close()

    def query(self, **kwargs) -> "SQLAlchemyConnector":
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

        self._cnt = query.count()

        # Order
        if order_info := kwargs["order_info"]:
            order_key = getattr(base_table.columns, order_info.key)
            query = query.order_by(getattr(sqlalchemy, order_info.order.lower())(order_key))

        # Paging
        if page_info := kwargs["page_info"]:
            per_page = page_info.per_page
            cur_page = page_info.cur_page
            query = query.limit(per_page).offset((cur_page - 1) * per_page)

        self._q = query
        self._column_names = [column.name for column in base_table.columns]
        return self

    def all(self) -> Tuple[List[dict], int]:
        data = [dict(zip(self._column_names, data)) for data in self._q.all()]

        return data, self._cnt

    def first(self):
        data = self._q.first()
        return data

    def execute(self, **kwargs):
        """
        [
            {
                "method":"INSERT",
                "table_nm":"inqr_bas",
                "data":{
                    "id":"9bb29b2b-159e-4cee-89af-a80cfe6f0651",
                    "title":"test문의",
                    "sbst":"문으으으의",
                    "ctg_id":"INQR001",
                    "reg_user_nm":"테스터",
                    "cmpno":"dev-12346578",
                    "del_yn":"N",
                    "reg_user":"f142cdc2-207b-4eda-9e7d-2605e4e65571",
                    "reg_date":"NOW()",
                    "amd_user":"f142cdc2-207b-4eda-9e7d-2605e4e65571",
                    "amd_date":"NOW()"
                }
            }
        ]
        [
            {
                "method":"UPDATE",
                "table_nm":"inqr_bas",
                "key": ["id"],
                "data":{
                    "id":"9bb29b2b-159e-4cee-89af-a80cfe6f0651",
                    "title":"test문의111111",
                    "sbst":"문으으으의"
                }
            }
        ]
        [
            {
                "method":"DELETE",
                "table_nm":"inqr_bas",
                "key": ["id"],
                "data":{
                    "id":"9bb29b2b-159e-4cee-89af-a80cfe6f0651"
                }
            }
        ]

        {"result":1,"errorMessage":""}
        """
        # try:
        #     session.begin()

        #     for row in params:
        #         method = row.method.lower()
        #         table = db.get_table(row.table_nm)
        #         cond = [getattr(table.columns, k) == row.data[k] for k in row.key] if row.key else []

        #         if method == "insert":
        #             ins = table.insert().values(**row.data)
        #             session.execute(ins)
        #         elif method == "update":
        #             stmt = table.update().where(*cond).values(**row.data)
        #             session.execute(stmt)
        #         elif method == "delete":
        #             stmt = table.delete().where(*cond)
        #             session.execute(stmt)
        #         else:
        #             raise NotImplementedError

        #     session.commit()
        # except Exception as e:
        #     session.rollback()
        #         raise e

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

    def get_column_info(self, table_nm) -> List[Dict[str, str]]:
        ...

class TiberoConnector(Connector):
    def __init__(self, app: FastAPI = None, **kwargs):
        self.conn = None
        self.cur = None
        self._q = None
        self._cntq = None
        if app is not None:
            self.init_app(app, kwargs)

    def init_app(self, app: FastAPI, **kwargs):
        self.conn = pyodbc.connect(kwargs.get("DB_URL"), autocommit=False)
        self.conn.setdecoding(pyodbc.SQL_CHAR, encoding="utf-8")
        self.conn.setdecoding(pyodbc.SQL_WCHAR, encoding="utf-32le")
        self.conn.setdecoding(pyodbc.SQL_WMETADATA, encoding="utf-32le")
        self.conn.setencoding(encoding="utf-8")

    def get_db(self) -> "TiberoConnector":
        self.cur = self.conn.cursor()
        try:
            yield self
        finally:
            if self._q:
                self._q = None
                self._cntq = None
            if self.cur:
                self.cur.close()

    def query(self, **kwargs) -> "TiberoConnector":
        """
        SELECT *
            FROM (
            SELECT ROWNUM AS rn, subquery.*
            FROM (
                SELECT *
                FROM ACT_SRVY
                JOIN ACT_SRV_FILE_DETLS ON ACT_SRVY.IDX = ACT_SRV_FILE_DETLS.IDX
                WHERE ACT_SRVY.OFANSTP = 'CMPLT'
            ) AS subquery
            ) AS main_query
            WHERE main_query.rn > 0;
        """
        table_nm = kwargs.get("table_nm")
        join_key = kwargs.get("key")

        join_clause = ""
        if join_info := kwargs.get("join_info"):
            t = join_info["table_nm"]
            k = join_info["key"]
            join_clause += f"join {t} on {table_nm}.{join_key} = {t}.{k} "

        where_clause = ""
        if where_info := kwargs.get("where_info"):
            where_clause += f"where "
            for info in where_info:
                t = info["table_nm"]
                k = info["key"]
                val = info["value"]
                op = info["op"]
                where_clause += f"{op} {self._calc_operand(f'{t}.{k}', val, info['compare_op'])} "
            # TODO: sub where conditions

        order_clause = ""
        if order_info := kwargs.get("order_info"):
            t = order_info["table_nm"]
            k = order_info["key"]
            o = order_info["order"]
            order_clause += f"order by {t}.{k} {str(o).upper()} "

        query = f"select * from {table_nm} " + join_clause + where_clause + order_clause
        self._cntq = f"select count(*) from {table_nm} " + join_clause + where_clause + order_clause

        page_clause = ""
        if page_info := kwargs.get("page_info"):
            per_page = page_info["per_page"]
            offset = (page_info["cur_page"] - 1) * per_page
            limit = offset + per_page
            page_clause += "select * from (select ROWNUM as SEQ, sq.* "
            page_clause += f"from ({query}) as sq) as mq where mq.SEQ > {offset} and mq.SEQ <= {limit}"
            query = page_clause

        self._q = query
        logger.info(query)
        return self

    def all(self) -> Tuple[List[dict], int]:
        try:
            data = self.cur.execute(self._q).fetchall()
            if data:
                rows = [dict(zip(self._get_headers(), row)) for row in data]
                return rows, int(self.cur.execute(self._cntq).fetchone()[0])
        except TypeError as te:
            logger.warning(te)
            return
        except Exception as e:
            raise e

    def first(self) -> Dict:
        try:
            data = self.cur.execute(self._q).fetchone()
            if data:
                return dict(zip(self._get_headers(), data))
        except TypeError as te:
            logger.warning(te)
            return
        except Exception as e:
            raise e

    def execute(self, **kwargs):
        try:
            method = str(kwargs.get("method")).lower()
            data = kwargs.get("data")
            params = tuple(data.values())

            query = ""
            if method == "insert":
                query += f"insert into {kwargs.get('table_nm')} "
                query += f"({','.join(data.keys())}) "
                query += f"values ({','.join(['?']*len(data))})"
            elif method == "update":
                query += f"update {kwargs.get('table_nm')} "
                query += f"set {','.join([f'{k} = ?' for k in data.keys()])} "

                k0, *ks = kwargs.get("key")
                query += f"where {k0} = '{data[k0]}' "
                if ks:
                    for k in ks:
                        query += f"and {k} = '{data[k]}' "
            elif method == "delete":
                query += f"delete from {kwargs.get('table_nm')} "
                query += f"where {' and '.join([f'{k} = ?' for k in kwargs.get('key')])}"

            else:
                raise Exception(f"{method} :: Mehtod not allowed")

            logger.info(f"query :: {query}")
            self.cur.execute(query, params)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e

    def _get_headers(self) -> list[str]:
        return [d[0].lower() for d in self.cur.description]

    def _calc_operand(self, k, v, operand):
        if operand in ["Equal", "="]:
            return f"{k} = '{v}'"
        elif operand in ["Not Equal", "!="]:
            return f"{k} != '{v}'"
        elif operand in ["Greater Than", ">"]:
            return f"{k} > '{v}'"
        elif operand in ["Greater Than or Equal", ">="]:
            return f"{k} >= '{v}'"
        elif operand in ["Less Than", "<"]:
            return f"{k} < '{v}'"
        elif operand in ["Less Than or Equal", "<="]:
            return f"{k} <='{v}'"
        elif operand.lower() in ["ilike"]:
            return f"upper({k}) like '{v}'"
        elif operand.lower() in ["in"]:
            v = ",".join([f"'{x}'" for x in v.split(",")])
            return f"{k} in ({v})"
        else:
            return f"{k} {operand} '{v}'"

    def get_column_info(self, table_nm) -> List[Dict[str, str]]:
        # OWNER, TABLE_NAME, COLUMN_NAME, COMMENT
        query = f"SELECT * FROM ALL_COL_COMMENTS WHERE TABLE_NAME = '{table_nm.upper()}';"
        logger.info(query)
        self.cur.execute(query)
        return [{"column_name": str(row[2]).lower(), "kor_column_name": row[3]} for row in self.cur.fetchall()]
