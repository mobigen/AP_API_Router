import os
import configparser
import argparse
from fastapi.logger import logger
from pathlib import Path
from tkinter.messagebox import NO
from typing import Any
from ApiService.ApiServiceConfig import config
from ConnectManager import PostgreManager
from retry import retry
import psycopg2


def get_config(root_path: str, config_name: str):
    ano_cfg = {}

    config = configparser.ConfigParser()
    config.read(os.path.join(root_path,
                             f"API-SERVICE/conf/{config_name}"), encoding='utf-8')
    for section in config.sections():
        ano_cfg[section] = {}
        for option in config.options(section):
            ano_cfg[section][option] = config.get(section, option)

    return ano_cfg


def parser_params() -> Any:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=int, default=19000)
    parser.add_argument("--db_type", default="postgresql")

    return parser.parse_args()


def prepare_config() -> None:
    args = parser_params()
    config.root_path = Path(os.getcwd()).parent
    api_router_cfg = get_config(config.root_path, "config.ini")
    config.api_config = get_config(config.root_path, "api_config.ini")
    config.db_type = args.db_type
    config.server_host = args.host
    config.server_port = args.port
    config.db_info = api_router_cfg[config.db_type]


@retry(psycopg2.OperationalError, delay=1, tries=3)
def connect_db(db_type, db_info):
    if db_type == "postgresql":
        db = PostgreManager(host=db_info["host"], port=db_info["port"],
                            user=db_info["user"], password=db_info["password"],
                            database=db_info["database"], schema=db_info["schema"])
    else:
        raise Exception(f'Not Implemented. ({db_type})')
    return db


def save_file_for_reload():
    with open(__file__, "a") as fd:
        fd.write(" ")


def make_res_msg(result, errorMessage, data=None, column_names=None):
    header_list = []
    for column_name in column_names:
        header = {"column_name": column_name}
        header_list.append(header)

    result = None
    if data == None or column_names == None:
        result = {"result": result, "errorMessage": errorMessage}
    else:
        result = {"result": result, "errorMessage": errorMessage,
                  "body": data, "header": header_list}
    return result
