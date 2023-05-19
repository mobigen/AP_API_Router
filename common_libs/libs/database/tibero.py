import datetime
import logging
from datetime import datetime
from typing import Dict, List, Tuple

import pyodbc
from fastapi import FastAPI

from .connector import Connector

logger = logging.getLogger()


class TiberoConnector(Connector):
    def __init__(self, app: FastAPI = None, **kwargs):
        self.conn = None
        self.cur = None
        self._q = None
        self._cntq = None
        if app is not None:
            self.init_app(app, kwargs)

    def init_app(self, app: FastAPI, **kwargs):
        def __convert_timestamp(value):
            value = datetime.strptime(value.decode(), '%Y/%m/%d %H:%M:%S.%f')
            return value.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        self.conn = pyodbc.connect(kwargs.get("DB_URL"), autocommit=False)
        self.conn.setdecoding(pyodbc.SQL_CHAR, encoding="utf-8")
        self.conn.setdecoding(pyodbc.SQL_WCHAR, encoding="utf-32le")
        self.conn.setdecoding(pyodbc.SQL_WMETADATA, encoding="utf-32le")
        self.conn.add_output_converter(pyodbc.SQL_TYPE_TIMESTAMP, __convert_timestamp)
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

    def _calc_operand(self, k, v, operand) -> str:
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
