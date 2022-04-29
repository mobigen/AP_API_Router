import logging
from typing import Dict, List
import importlib.util
from fastapi import APIRouter
from ApiRoute.ApiRouteConfig import config
from ConnectManager import RemoteCmd
from Utils.DataBaseUtil import convert_data
from Utils.CommonUtil import connect_db, make_res_msg, save_file_for_reload
from pydantic import BaseModel
from starlette.requests import Request
import traceback

#logger = logging.getLogger()

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
    def __init__(self) -> None:
        self.router = APIRouter()
        self.set_route()

    def set_route(self) -> None:
        self.router.add_api_route("/api/getApiList", self.get_api_list, methods=["GET"])
        self.router.add_api_route("/api/getApi", self.get_api, methods=["GET"])
        self.router.add_api_route("/api/setApi", self.set_api, methods=["POST"])
        self.router.add_api_route("/api/delApi", self.del_api, methods=["POST"])

        db = connect_db(config.db_type, config.db_info)
        api_info, _ = db.select('SELECT * FROM api_info;')
        
        for api in api_info:
            self.router.add_api_route(f'/api/{api["api_name"]}', self.route_api, methods=["POST"], tags=["route"])
        
        for api_name, api_info in config.api_config.items():
            module_path = f'{config.root_path}/AP_API_Router/API-ROUTER/ApiList/{api_name}.py'
            module_name = "api"
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.router.add_api_route(f'{api_info["url_prefix"]}/{api_name}', module.api, methods=[api_info["method"]], tags=["service"])
        

    def get_api_list(self) -> Dict:
        api_info_query = f'SELECT * FROM api_info;'
        api_params_query = f'SELECT * FROM api_params;'
        
        db = connect_db(config.db_type, config.db_info)

        api_info, column_names = db.select(api_info_query)
        api_info = make_res_msg("", "", api_info, column_names)
        
        api_params, column_names = db.select(api_params_query)
        api_params = make_res_msg("", "", api_params, column_names)

        return {"api_info" : api_info, "api_params" : api_params}
    
    
    def get_api(self, api_name:str) -> Dict:
        api_info_query = f'SELECT * FROM api_info WHERE api_name = {convert_data(api_name)};'
        api_params_query = f'SELECT * FROM api_params WHERE api_name = {convert_data(api_name)};'

        db = connect_db(config.db_type, config.db_info)
                            
        api_info, column_names = db.select(api_info_query)
        api_info = make_res_msg("", "", api_info, column_names)
                            
        api_params, column_names = db.select(api_params_query)
        api_params = make_res_msg("", "", api_params, column_names)

        return {"api_info" : api_info, "api_params" : api_params}
    
        
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
        
        save_file_for_reload()
            
        return {"API_NAME : set_api"}      

    def del_api(self, api_name:str) -> Dict:
        db = connect_db(config.db_type, config.db_info)

        db.delete("api_info", {"api_name" : api_name})
        db.delete("api_params", {"api_name" : api_name})

        save_file_for_reload()

        return {"API_NAME : del_api"}

    async def route_api(self, request:Request) -> Dict:
        try:
            api_name = request.url.path.split("/")[-1]
            api_info_query = f'SELECT * FROM api_info WHERE api_name = {convert_data(api_name)};'        
            api_params_query = f'SELECT * FROM api_params WHERE api_name = {convert_data(api_name)};'

            db = connect_db(config.db_type, config.db_info)        
            api_info, _ = db.select(api_info_query)
            api_params, _ = db.select(api_params_query)
        
            if len(api_info) == 0:
                return {"result" : 0, "errorMessage" : "This is an unregistered API."}
 
            api_info = api_info[0]
            msg_type = api_info["msg_type"]
            if msg_type == "JSON":
                request_body = await request.json()
            elif msg_type == "BINARY":
                request_body = await request.form() #request.body()
            else:
                # Unknown Type
                pass    
    
            if api_info["bypass"] == "ON":
                #send req
                method = api_info["method"]
            else:
                #call remote func
                remote_cmd = RemoteCmd(config.remote_info["host"], config.remote_info["port"], config.remote_info["id"], config.remote_info["password"])
                #make command (use params + body)
                remote_cmd.cmd_exec(api_info["command"])
        except Exception:
            print(traceback.format_exc())
        return eval(remote_cmd.cmd_exec(api_info["command"]))
    
       