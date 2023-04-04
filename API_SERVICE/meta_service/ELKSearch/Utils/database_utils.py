import logging
import logging.config
import os
import argparse
import configparser
from psycopg2 import pool
from typing import List, Dict, Tuple, Any
from Manager.manager import ElasticSearchManager


class ElsSearchConfig:
    root_path: str
    category: str

    db_type: str
    db_info: Dict

    els_type: str
    els_info: Dict
    check: bool

    conn_pool: pool.SimpleConnectionPool
    es: ElasticSearchManager


config = ElsSearchConfig


def get_config(root_path, config_name: str):
    ano_cfg = {}

    conf = configparser.ConfigParser()
    config_path = root_path + f"/ELKSearch/conf/{config_name}"
    conf.read(config_path, encoding="utf-8")
    for section in conf.sections():
        ano_cfg[section] = {}
        for option in conf.options(section):
            ano_cfg[section][option] = conf.get(section, option)

    return ano_cfg


def parser_params() -> Any:
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", default="local")
    parser.add_argument("--db_type", default="local")
    parser.add_argument("--check", default="True")

    return parser.parse_args()


def prepare_config(root_path) -> None:
    args = parser_params()
    config.root_path = root_path
    config.category = args.category

    db_config = get_config(root_path, "db_config.ini")
    els_config = get_config(root_path, "config.ini")

    config.els_type = args.category
    config.els_info = els_config[args.category]
    if args.category not in ['email','ranking']:
        config.es = ElasticSearchManager(**config.els_info)
    config.check = args.check

    config.db_type = f"{args.db_type}_db"
    config.db_info = db_config[config.db_type]
    config.conn_pool = make_connection_pool(config.db_info)


def make_connection_pool(db_info):
    conn_pool = pool.SimpleConnectionPool(
        1,
        20,
        user=db_info["user"],
        password=db_info["password"],
        host=db_info["host"],
        port=db_info["port"],
        database=db_info["database"],
        options=f'-c search_path={db_info["schema"]}',
        connect_timeout=10,
    )
    return conn_pool


def connect_db():
    conn = config.conn_pool.getconn()
    return conn


def execute(conn, cursor, sql) -> None:
    cursor.execute(sql)
    conn.commit()


def select(conn, sql: str, count: int = None) -> Tuple[List[Dict[Any, Any]], List[Any]]:
    cursor = conn.cursor()
    execute(conn, cursor, sql)
    column_names = [desc[0] for desc in cursor.description]
    if count is None:
        rows = cursor.fetchall()
    else:
        rows = cursor.fetchmany(count)

    result = []
    for row in rows:
        result.append(dict(zip(column_names, row)))
    return result, column_names


def set_log(root_path):
    log_dir = f"{root_path}/log/cron"
    if os.path.isdir(log_dir):
        print("Directory Exists")
    else:
        print(f"Make log dir : {log_dir}")
        os.makedirs(log_dir)

    parser = configparser.ConfigParser()
    parser.read(
        f"{config.root_path}/ELKSearch/conf/logging.conf", encoding="utf-8"
    )

    parser.set(
        "handler_rotatingFileHandler",
        "args",
        f"('{config.root_path}/log/cron/cron.log', 'a', 20000000, 10)",
    )

    with open(f"{config.root_path}/ELKSearch/conf/logging.conf", "w") as f:
        parser.write(f)

    logging.config.fileConfig(parser)
    logger = logging.getLogger("cron")
    return logger
