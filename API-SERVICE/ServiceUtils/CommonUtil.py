from datetime import datetime, timedelta
from ServiceUtils.exceptions import TokenDoesNotExist, InvalidUserInfo
from pytz import timezone
import configparser
import argparse
import traceback
from fastapi.logger import logger
from fastapi.requests import Request
from typing import Any, Optional, Dict
from ApiService.ApiServiceConfig import config
from ServiceConnectManager import PostgresManager
from psycopg2 import pool
import sys
from jose import jwt
import traceback
import logging

lamp = logging.getLogger("trace")


def get_token_from_cookie(request: Request):
    recv_access_token = request.cookies.get(config.secret_info["cookie_name"])
    if not recv_access_token:
        raise TokenDoesNotExist
    return recv_access_token


def jwt_decode(token):
    return jwt.decode(
        token=token,
        key=config.secret_info["secret_key"],
        algorithms=config.secret_info["algorithm"],
    )


def get_user_info(payload):
    username = payload[config.user_info["id_column"]]
    user = get_user(username)
    if not user[0]:
        raise InvalidUserInfo
    user = user[0][0]

    return user


def convert_data(data) -> str:
    data = str(data)
    if data:
        if data == "now()" or data == "NOW()":
            return data
        if data[0] == "`":
            return data[1:]
    return f"'{data.strip()}'"


def set_log_path():
    parser = configparser.ConfigParser()
    parser.read(f"{config.root_path}/conf/{config.category}/logging.conf", encoding="utf-8")

    parser.set(
        "handler_rotatingFileHandler",
        "args",
        f"('{config.root_path}/log/{config.category}/{config.category}.log', 'a', 20000000, 10)",
    )

    with open(f"{config.root_path}/conf/{config.category}/logging.conf", "w") as f:
        parser.write(f)


def get_config(config_name: str):
    ano_cfg = {}

    conf = configparser.ConfigParser()
    config_path = config.root_path + f"/conf/{config.category}/{config_name}"
    conf.read(config_path, encoding="utf-8")
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


def prepare_config(root_path) -> None:
    args = parser_params()
    config.root_path = root_path
    config.category = args.category
    api_router_cfg = get_config("config.ini")
    config.api_config = get_config("api_config.ini")
    config.server_host = args.host
    config.server_port = args.port
    config.db_type = f"{args.db_type}_db"
    config.db_info = api_router_cfg[config.db_type]
    config.lamp_info = api_router_cfg["lamp_info"]
    config.conn_pool = make_connection_pool(config.db_info)
    if config.category == "common":
        config.secret_info = api_router_cfg["secret_info"]
        config.user_info = api_router_cfg["user_info"]
        config.ldap_info = api_router_cfg["ldap_info"]


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
    db = PostgresManager()
    return db


def save_file_for_reload():
    with open(__file__, "a") as fd:
        fd.write(" ")


def make_res_msg(result, err_msg, data=None, column_names=None, kor_column_names=None):
    header_list = []
    for index, column_name in enumerate(column_names):
        if kor_column_names:
            header = {
                "column_name": column_name,
                "kor_column_name": kor_column_names[index],
            }
        else:
            header = {"column_name": column_name}
        header_list.append(header)

    if data is None or column_names is None:
        res_msg = {"result": result, "errorMessage": err_msg}
    else:
        res_msg = {
            "result": result,
            "errorMessage": err_msg,
            "data": {"body": data, "header": header_list},
        }
    return res_msg


def get_exception_info():
    ex_type, ex_value, ex_traceback = sys.exc_info()
    trace_back = traceback.extract_tb(ex_traceback)
    trace_log = "\n".join([str(trace) for trace in trace_back])
    logger.error(
        f"\n- Exception Type : {ex_type}\n- Exception Message : {str(ex_value).strip()}\n- Exception Log : \n{trace_log}"
    )
    return ex_type.__name__


def convert_error_message(exception_name: str):
    error_message = None
    if exception_name == "UniqueViolation":
        error_message = "UNIQUE_VIOLATION"
    else:
        error_message = exception_name

    return error_message


##### for user info #####
class IncorrectUserName(Exception):
    pass


class IncorrectPassword(Exception):
    pass


def get_user(user_name: str, user_type: str = None):
    db = connect_db()
    query = (
        f'SELECT * FROM {config.user_info["table"]} WHERE {config.user_info["id_column"]} = {convert_data(user_name)}'
    )
    query += f" and user_type = '{user_type}'" if user_type else ""
    user = db.select(query)
    return user


def create_token(data: dict, secret_key, algorithm, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone("Asia/Seoul")) + expires_delta
    else:
        expire = datetime.now(timezone("Asia/Seoul")) + timedelta(minutes=15)

    logger.info(f"commonToken Expire : {expire}")
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, secret_key, algorithm=algorithm)


def make_token_data(user: Dict) -> Dict:
    token_data_column = config.secret_info["token_data_column"].split(",")
    # token_data = {column: user[column] for column in token_data_column}
    token_data = {
        column: datetime.strftime(user[column], "%Y-%m-%d %H:%M:%S.%f")
        if isinstance(user[column], datetime)
        else user[column]
        for column in token_data_column
    }
    logger.info(token_data)
    return token_data


def kt_lamp(
    log_type: str,
    transaction_id: str,
    operation: str,
    res_type: str = "I",
    res_code: str = "",
    res_desc: str = "",
):
    lamp_form = {}
    now = datetime.now()
    lamp_form["timestamp"] = now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    lamp_form["service"] = config.lamp_info["service_code"]
    lamp_form["operation"] = f'{config.lamp_info["prefix"]}_{operation}'
    lamp_form["transactionId"] = transaction_id
    lamp_form["logType"] = log_type

    lamp_form["host"] = {}
    lamp_form["host"]["name"] = config.lamp_info["host_name"]
    lamp_form["host"]["ip"] = config.lamp_info["host_ip"]

    if log_type == "OUT_REQ":
        lamp_form["destination"] = {}
        lamp_form["destination"]["name"] = config.lamp_info["dest_name"]
        lamp_form["destination"]["ip"] = config.lamp_info["dest_ip"]
    elif log_type == "OUT_RES" or log_type == "IN_RES":
        lamp_form["response"] = {}
        lamp_form["response"]["type"] = res_type
        lamp_form["response"]["code"] = res_code
        lamp_form["response"]["desc"] = res_desc

    lamp.info(lamp_form)
