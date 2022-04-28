import logging
from typing import Dict, List
import importlib.util
import traceback
from fastapi import APIRouter
from ApiRoute.ApiRouteConfig import config
from ConnectManager import RemoteCmd
from Utils.DataBaseUtil import convert_data
from Utils.CommonUtil import connect_db, make_res_msg
from pydantic import BaseModel
from starlette.requests import Request

logger = logging.getLogger()

class ApiParam(BaseModel):
    api_name: str
    param_name: str
    data_type: str
    default_value: str

class ApiInfo(BaseModel):
    api_name: str
    category: str
    url: str
    msg_type: str
    method: str
    protocol: str
    command: str
    bypass: str
    params: List[ApiParam]

class ApiRoute:
    def __init__(self, db_type:str, db_info: Dict, remote_info: Dict) -> None:
        #self.db_type = db_type
        #self.db_info = db_info
        #self.remote_info = remote_info
        
        self.router = APIRouter()
        self.set_route()

    def set_route(self) -> None:
        self.router.add_api_route("/api/getApiList", self.get_api_list, methods=["GET"])
        self.router.add_api_route("/api/setApi", self.set_api, methods=["POST"])
        
        api_info_query = 'SELECT * FROM api_info;'
        db = connect_db(config.db_type, config.db_info)
        api_info, _ = db.select(api_info_query)
        for api in api_info:
            self.router.add_api_route(f'/api/{api["api_name"]}', self.route_api, methods=["POST"])

        '''
        for api_name, api_info in config.api_config.items():
            module_path = f'{config.root_path}/AP_API_Router/API-ROUTER/ApiList/{api_name}.py'
            module_name = "api"
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.router.add_api_route(f'{api_info["url_prefix"]}/{api_name}', module.api, methods=[api_info["method"]])
        '''
        
    def set_api(self, api_info:ApiInfo) -> Dict:
        db = connect_db(config.db_type, config.db_info)
        
        insert_api_info = {}
        insert_api_params = []
        for key, value in api_info.__dict__.items():
            if key == "params":
                for param in value:
                    insert_api_params.append(param.__dict__)
            else:
                insert_api_info[key] = value

        db.insert("api_info", [insert_api_info])
        db.insert("api_params", insert_api_params)

        self.router.add_api_route(f'/api/{insert_api_info["api_name"]}', self.route_api, methods=[{insert_api_info["method"]}])

        return {"API_NAME" : "setApi"}      

    def get_api_list(self) -> Dict:
        api_info_query = f'SELECT * FROM api_info;'
        api_params_query = f'SELECT * FROM api_params;'
        
        db = connect_db(config.db_type, config.db_info)

        api_info, column_names = db.select(api_info_query)
        api_info = make_res_msg("", "", api_info, column_names)
        
        api_params, column_names = db.select(api_params_query)
        api_params = make_res_msg("", "", api_params, column_names)

        return {"api_info" : api_info, "api_params" : api_params}

    def route_api(self, request:Request) -> Dict:
        print("API : ", request.url.path)
        '''
            try:
                db = connect_db(config.db_type, config.db_info)        


                #search_query = f'SELECT * FROM api_info WHERE api_name = {convert_data(api_name)};'        
                #api_info, _ = db.select(search_query)
            except Exception:
                print(traceback.format_exc())
            if len(api_info) == 0:
                return {"result" : 0, "errorMessage" : "This is an unregistered API."}
        '''
        #remote_cmd = RemoteCmd(self.remote_info["host"], self.remote_info["port"], self.remote_info["id"], self.remote_info["password"])
        #return eval(remote_cmd.cmd_exec(api_info[0]["command"]))
        return {"API_NAME" : "Router"}
    
