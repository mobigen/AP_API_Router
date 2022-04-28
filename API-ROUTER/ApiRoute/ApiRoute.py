import logging
from typing import Dict, List
import importlib.util
import traceback
from fastapi import APIRouter
from ApiRoute.ApiRouteInfo import config
from ConnectManager import RemoteCmd
from Utils.CommonUtil import connect_db
from Utils.DataBaseUtil import convert_data

logger = logging.getLogger()

class ApiRoute:
    def __init__(self, db_type:str, db_info: Dict, remote_info: Dict) -> None:
        self.db_type = db_type
        self.db_info = db_info
        self.remote_info = remote_info
        
        self.router = APIRouter()
        self.set_route()

    def set_route(self) -> None:
        for api_name, api_info in config.api_config.items():
            module_path = f'{config.root_path}/AP_API_Router/API-ROUTER/ApiList/{api_name}.py'
            module_name = "api"
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.router.add_api_route(f'{api_info["url_prefix"]}/{api_name}', module.api, methods=[api_info["method"]])

    
    def route_api(self, api_name:str) -> Dict:
        db = connect_db()
        search_query = f'SELECT * FROM {config.db_info["schema"]}.{config.db_info["api_info_table"]} \
                        WHERE api_name = {convert_data(api_name)};'        
        api_info, _ = db.select(search_query)

        if len(api_info) == 0:
            return {"result" : 0, "errorMessage" : "This is an unregistered API."}

        remote_cmd = RemoteCmd(self.remote_info["host"], self.remote_info["port"], self.remote_info["id"], self.remote_info["password"])
        return eval(remote_cmd.cmd_exec(api_info[0]["command"]))

    
