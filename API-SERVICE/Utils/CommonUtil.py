from datetime import datetime, timedelta
from pytz import timezone
import os
import configparser
import argparse
from fastapi.logger import logger
from pathlib import Path
from typing import Any, Optional, Dict
from passlib.context import CryptContext
from psycopg2 import pool
import jwt
import sys
import traceback
from ApiService.ApiServiceConfig import config
from ConnectManager import PostgresManager


def convert_data(data) -> str:
    data = str(data)
    if data:
        if data == "now()" or data == "NOW()":
            return data
        if data[0] == "`":
            return data[1:]
    return f'\'{data.strip()}\''


def set_log_path():
    parser = configparser.ConfigParser()
    parser.read(
        f'{config.root_path}/conf/{config.category}/logging.conf', encoding='utf-8')

    parser.set("handler_rotatingFileHandler", "args",
               f"('{config.root_path}/log/{config.category}/{config.category}.log', 'a', 20000000, 10)")

    with open(f'{config.root_path}/conf/{config.category}/logging.conf', 'w') as f:
        parser.write(f)


def get_config(config_name: str):
    ano_cfg = {}

    conf = configparser.ConfigParser()
    config_path = config.root_path+f"/conf/{config.category}/{config_name}"
    conf.read(config_path, encoding='utf-8')
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
    parser.add_argument("--db_type", default="test")

    return parser.parse_args()


def prepare_config() -> None:
    args = parser_params()
    config.root_path = str(
        Path(os.path.dirname(os.path.abspath(__file__))).parent)
    config.category = args.category
    api_router_cfg = get_config("config.ini")
    config.api_config = get_config("api_config.ini")
    config.server_host = args.host
    config.server_port = args.port
    config.db_type = f'{args.db_type}_db'
    config.db_info = api_router_cfg[config.db_type]
    config.conn_pool = make_connection_pool(config.db_info)
    if config.category == "common":
        config.secret_info = api_router_cfg["secret_info"]
        config.user_info = api_router_cfg["user_info"]
        config.pwd_context = CryptContext(
            schemes=["bcrypt"], deprecated="auto")
        config.email_auth = api_router_cfg["email_auth"]


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
    with open(__file__, "a") as fd:
        fd.write(" ")


def make_res_msg(result, err_msg, data=None, column_names=None, kor_column_names=None):
    header_list = []
    for index, column_name in enumerate(column_names):
        if kor_column_names:
            header = {"column_name": column_name,
                      "kor_column_name": kor_column_names[index]}
        else:
            header = {"column_name": column_name}
        header_list.append(header)

    if data is None or column_names is None:
        res_msg = {"result": result, "errorMessage": err_msg}
    else:
        res_msg = {"result": result, "errorMessage": err_msg,
                   "data": {"body": data, "header": header_list}}
    return res_msg


def get_exception_info():
    ex_type, ex_value, ex_traceback = sys.exc_info()
    trace_back = traceback.extract_tb(ex_traceback)
    trace_log = "\n".join([str(trace) for trace in trace_back])
    logger.error(
        f'\n- Exception Type : {ex_type}\n- Exception Message : {str(ex_value).strip()}\n- Exception Log : \n{trace_log}')
    return ex_type.__name__


def convert_error_message(exception_name: str):
    error_message = None
    if exception_name == "UniqueViolation":
        error_message = "UNIQUE_VIOLATION"
    else:
        error_message = exception_name

    return error_message


##### for user info #####
def get_user(user_name: str):
    db = connect_db()
    user = db.select(
        f'SELECT * FROM {config.user_info["table"]} WHERE {config.user_info["id_column"]} = {convert_data(user_name)}')
    return user


def create_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone('Asia/Seoul')) + expires_delta
    else:
        expire = datetime.now(timezone('Asia/Seoul')) + timedelta(minutes=15)

    logger.info(f'commonToken Expire : {expire}')
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode, config.secret_info["secret_key"], algorithm=config.secret_info["algorithm"])
    return encoded_jwt


def make_token_data(user: Dict) -> Dict:
    token_data_column = config.secret_info["token_data_column"].split(",")
    token_data = {column: user[column] for column in token_data_column}
    return token_data


class IncorrectUserName(Exception):
    pass


class IncorrectPassword(Exception):
    pass


def verify_password(plain_password, hashed_password):
    return config.pwd_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user[0]:
        raise IncorrectUserName

    user = user[0][0]
    if not verify_password(password, user[config.user_info["password_column"]]):
        raise IncorrectPassword
    return user
