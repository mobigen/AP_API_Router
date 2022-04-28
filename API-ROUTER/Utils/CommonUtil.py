import os
import configparser
import logging
from pathlib import Path
from ConnectManager import PostgreManager
from ApiRoute.ApiRouteInfo import config

logger = logging.getLogger()

def get_config(root_path:str, config_name:str):
    ano_cfg = {}

    config = configparser.ConfigParser()
    config.read(os.path.join(root_path,
                             f"AP_API_Router/API-ROUTER/conf/{config_name}"), encoding='utf-8')
    for section in config.sections():
        ano_cfg[section] = {}
        for option in config.options(section):
            ano_cfg[section][option] = config.get(section, option)

    return ano_cfg

def prepare_config():
    config.root_path = Path(os.getcwd()).parent
    api_router_cfg = get_config(config.root_path, "config.ini")
    config.api_config = get_config(config.root_path, "api_config.ini")
    config.db_type = api_router_cfg["default"]["db"]
    config.db_info = api_router_cfg[config.db_type]
    config.remote_info = api_router_cfg["remote"]
    config.server_host = api_router_cfg["default"]["host"]
    config.server_port = int(api_router_cfg["default"]["port"])

def connect_db(db_type, db_info):
    if db_type == "postgresql":
        db = PostgreManager(host=db_info["host"], port=db_info["port"],
                        user=db_info["user"], password=db_info["password"], 
                        database=db_info["database"], schema=db_info["schema"])
    else:
        logger.error(f"Not Implemented. {db_type}")
    return db

def make_res_msg(result, errorMessage, data, column_names):    
    header_list = []
    for column_name in column_names:
        header = {"column_name" : column_name} 
        header_list.append(header)          
    
    return {"result" : result, "errorMessage" : errorMessage, "body" : data, "header" : header_list}