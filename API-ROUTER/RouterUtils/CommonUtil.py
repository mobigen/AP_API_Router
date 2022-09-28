import os
import configparser
import argparse
import starlette.datastructures
from fastapi.logger import logger
from typing import Any, Dict, List
from ApiRoute.ApiRouteConfig import config
from RouterConnectManager import PostgresManager
from psycopg2 import pool
import sys
import traceback

def convert_data(data) -> str:
    return f'\'{str(data)}\''

def set_log_path():
    parser = configparser.ConfigParser()
    parser.read(f'{config.root_path}/conf/logging.conf', encoding='utf-8')

    parser.set("handler_rotatingFileHandler", "args",
               f"('{config.root_path}/log/API-Router.log', 'a', 20000000, 10)")

    with open(f'{config.root_path}/conf/logging.conf', 'w') as f:
        parser.write(f)

def get_config(config_name: str):
    ano_cfg = {}

    conf = configparser.ConfigParser()
    config_path =config.root_path+f'/conf/{config_name}'
    conf.read(config_path, encoding = 'utf-8')
    for section in conf.sections():
        ano_cfg[section]={}
        for option in conf.options(section):
            ano_cfg[section][option]=conf.get(section, option)

    return ano_cfg


def parser_params() -> Any:
    parser=argparse.ArgumentParser()
    parser.add_argument("--host", type = str, default = "127.0.0.1")
    parser.add_argument("--port", type = int, default = 18000)
    parser.add_argument("--db_type", default = "test")

    return parser.parse_args()


def prepare_config(root_path) -> None:
    args = parser_params()
    config.root_path = root_path
    api_router_cfg=get_config("config.ini")
    config.api_config=get_config("api_config.ini")
    config.db_type=f'{args.db_type}_db'
    config.server_host=args.host
    config.server_port=args.port
    config.db_info=api_router_cfg[config.db_type]
    config.conn_pool = make_connection_pool(config.db_info)
    config.remote_info=api_router_cfg["remote"]
    config.secret_info=api_router_cfg["secret_info"]

def make_connection_pool(db_info):
    conn_pool = pool.SimpleConnectionPool(1, 20, user=db_info["user"],
                                          password=db_info["password"],
                                          host=db_info["host"],
                                          port=db_info["port"],
                                          database=db_info["database"],
                                          options=f'-c search_path={db_info["schema"]}', connect_timeout=10)
    return conn_pool

def connect_db():
    db = PostgresManager()
    return db

def save_file_for_reload():
    with open(f'{config.root_path}/server.py', "a") as fd:
        fd.write(" ")

def make_res_msg(result, err_msg, data = None, column_names = None):
    header_list=[]
    for column_name in column_names:
        header={"column_name": column_name}
        header_list.append(header)

    if data is None or column_names is None:
        res_msg={"result": result, "errorMessage": err_msg}
    else:
        res_msg={"result": result, "errorMessage": err_msg,
                   "body": data, "header": header_list}
    return res_msg



def get_exception_info():
    ex_type, ex_value, ex_traceback = sys.exc_info()
    trace_back = traceback.extract_tb(ex_traceback)
    trace_log = "\n".join([str(trace) for trace in trace_back])
    logger.error(
        f'\n- Exception Type : {ex_type}\n- Exception Message : {str(ex_value).strip()}\n- Exception Log : \n{trace_log}')
    return ex_type.__name__

def delete_headers(headers: Dict, delete_header: List) -> Dict:
    for delete in delete_header:
        if headers.get(delete):
            del(headers[delete])
    return headers
          