import psycopg2
from typing import List, Dict
from fastapi.logger import logger
from Utils.DataBaseUtil import make_insert_query, make_update_query, make_delete_query


class PostgreManager:
    def __init__(self, host: str, port: str, user: str, password: str, database: str, schema: str) -> None:
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.schema = schema
        self.conn = self.connect()
        self.cursor = self.conn.cursor()

    def connect(self):
        conn = psycopg2.connect(host=self.host, port=self.port, user=self.user,
                                password=self.password, database=self.database,
                                options=f"-c search_path={self.schema}")
        logger.debug("PostgreManager Connect.")
        return conn

    def execute(self, sql: str) -> None:
        self.cursor.execute(sql)
        self.conn.commit()
        logger.debug(f'PostgreManager Execute Result. ({sql})')

    def select(self, sql: str, count: int = None) -> List[Dict]:
        self.execute(sql)
        column_names = [desc[0] for desc in self.cursor.description]
        if count == None:
            rows = self.cursor.fetchall()
        else:
            rows = self.cursor.fetchmany(count)
        logger.debug(f'PostgreManager Select Execute. ({sql})')

        result = []
        for row in rows:
            result.append(dict(zip(column_names, row)))
        return result, column_names

    def insert(self, table: str, into_info: List[Dict]) -> None:
        sql = make_insert_query(f"{self.schema}.{table}", into_info)
        self.execute(sql)
        logger.debug(f'PostgreManager Insert Execute. ({sql})')

    def update(self, table: str, set_info: Dict, where_info: Dict) -> None:
        sql = make_update_query(f"{self.schema}.{table}", set_info, where_info)
        self.execute(sql)
        logger.debug(f'PostgreManager Update Execute. ({sql})')

    def delete(self, table: str, where_info: Dict) -> None:
        sql = make_delete_query(f"{self.schema}.{table}", where_info)
        self.execute(sql)

        logger.debug(f'PostgreManager Delete Execute. ({sql})')

    def commit(self):
        self.conn.commit()

    def __del__(self) -> None:
        self.cursor.close()
        self.conn.close()
