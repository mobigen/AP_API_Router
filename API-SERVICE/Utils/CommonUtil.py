import os
import configparser
import argparse
import starlette.datastructures
from fastapi.logger import logger
from pathlib import Path
from typing import Any
from ApiService.ApiServiceConfig import config
from ConnectManager import PostgresManager
from retry import retry
import psycopg2
import jwt


def get_config(root_path: str, config_name: str):
    ano_cfg = {}

    conf = configparser.ConfigParser()
    conf.read(os.path.join(root_path,
                           f"API-SERVICE/conf/{config_name}"), encoding='utf-8')
    for section in conf.sections():
        ano_cfg[section] = {}
        for option in conf.options(section):
            ano_cfg[section][option] = conf.get(section, option)

    return ano_cfg


def parser_params() -> Any:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=int, default=19000)
    parser.add_argument("--category", default="meta")

    return parser.parse_args()


def prepare_config() -> None:
    args = parser_params()
    config.root_path = Path(os.getcwd()).parent
    api_router_cfg = get_config(config.root_path, "config.ini")
    config.api_config = get_config(config.root_path, "api_config.ini")
    config.category = args.category
    config.server_host = args.host
    config.server_port = args.port
    config.db_info = api_router_cfg[config.category]
    config.secret_info = api_router_cfg["secret_info"]


@retry(psycopg2.OperationalError, delay=1, tries=3)
def connect_db(db_info):
    db = PostgresManager(host=db_info["host"], port=db_info["port"],
                         user=db_info["user"], password=db_info["password"],
                         database=db_info["database"], schema=db_info["schema"])

    return db


def save_file_for_reload():
    with open(__file__, "a") as fd:
        fd.write(" ")


def make_res_msg(result, err_msg, data=None, column_names=None):
    header_list = []
    for column_name in column_names:
        header = {"column_name": column_name}
        header_list.append(header)

    if data is None or column_names is None:
        res_msg = {"result": result, "errorMessage": err_msg}
    else:
        res_msg = {"result": result, "errorMessage": err_msg,
                   "data": {"body": data, "header": header_list}}
    return res_msg


def get_token_info(headers: starlette.datastructures.Headers):
    user_info = None
    if config.secret_info["name"] in headers:
        user_info = jwt.decode(headers[config.secret_info["name"]],
                               config.secret_info["secret"], algorithms="HS256", options={"verify_exp": False})
    logger.debug(f'user info : {user_info}')
    return user_info
