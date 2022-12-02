import psycopg2
from typing import List, Dict, Tuple, Any
from fastapi.logger import logger
from ApiRoute.ApiRouteConfig import config


class PostgresManager:
    def __init__(self) -> None:
        self.conn = self.connect()
        self.cursor = self.conn.cursor()

    def connect(self):
        conn = config.conn_pool.getconn()

        logger.info("PostgresManager Connect.")
        return conn

    def execute(self, sql: str) -> None:
        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except (Exception, psycopg2.DatabaseError):
            self.conn.rollback()
            raise psycopg2.DatabaseError

    def multiple_excute(self, sql_list: list) -> None:
        try:
            for index, sql in enumerate(sql_list):
                logger.info(f"PostgresManager Multiple Execute. ({index}. {sql})")
                self.cursor.execute(sql)
            self.conn.commit()
        except (Exception, psycopg2.DatabaseError):
            self.conn.rollback()
            raise psycopg2.DatabaseError

    def select(
        self, sql: str, count: int = None
    ) -> Tuple[List[Dict[Any, Any]], List[Any]]:
        self.execute(sql)
        column_names = [desc[0] for desc in self.cursor.description]
        if count is None:
            rows = self.cursor.fetchall()
        else:
            rows = self.cursor.fetchmany(count)
        logger.info(f"PostgresManager Select Execute. ({sql})")

        result = []
        for row in rows:
            result.append(dict(zip(column_names, row)))
        return result, column_names

    def commit(self):
        self.conn.commit()

    def __del__(self) -> None:
        self.cursor.close()
        config.conn_pool.putconn(self.conn)
