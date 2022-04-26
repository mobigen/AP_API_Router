import logging
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, List

from regex import D
from ConnectManager import RemoteCmd, PostgreManager, DataBaseUtil
import traceback


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

def make_res_msg(result, errorMessage, data, column_names):    
    header_list = []
    for column_name in column_names:
        header = {"column_name" : column_name} 
        header_list.append(header)          
    
    return {"result" : result, "errorMessage" : errorMessage, "body" : data, "header" : header_list}

class ApiRoute:
    def __init__(self, db_type:str, db_info: Dict) -> None:
        self.db_type = db_type
        self.db_info = db_info
        
        self.router = APIRouter()
        self.set_route()

    def set_route(self) -> None:
        self.router.add_api_route("/api/get_all_info", self.get_all_api_info, methods=["GET"])
        self.router.add_api_route("/api/get_info", self.get_api_info, methods=["GET"])
        self.router.add_api_route("/api/set_info", self.set_api_info, methods=["POST"])
        self.router.add_api_route("/api/del_info", self.del_api_info, methods=["POST"])
        self.router.add_api_route("/api/route/{api_name}", self.route_api, methods=["POST"])

    def connect_db(self):
        if self.db_type == "postgresql":
            db = PostgreManager(host=self.db_info["host"], port=self.db_info["port"],
                            user=self.db_info["user"], password=self.db_info["password"], 
                            database=self.db_info["database"], schema=self.db_info["schema"])
        else:
            logger.error(f"Not Implemented. {self.db_type}")
        return db
        
    def get_all_api_info(self) -> Dict:
        db = self.connect_db()
        
        info_query = f'SELECT * FROM {self.db_info["schema"]}.{self.db_info["api_info_table"]};'
        api_info, column_names = db.select(info_query)
        api_info = make_res_msg("", "", api_info, column_names)
        
        params_query = f'SELECT * FROM {self.db_info["schema"]}.{self.db_info["api_params_table"]};'
        api_params, column_names = db.select(params_query)
        api_params = make_res_msg("", "", api_params, column_names)

        return {"api_info" : api_info, "api_params" : api_params}
    
    def get_api_info(self, api_name:str) -> Dict:
        db = self.connect_db()
        
        info_query = f'SELECT * FROM {self.db_info["schema"]}.{self.db_info["api_info_table"]} \
                        WHERE api_name = {DataBaseUtil.convert_data(api_name)};'
                        
        api_info, column_names = db.select(info_query)
        api_info = make_res_msg("", "", api_info, column_names)
        
        params_query = f'SELECT * FROM {self.db_info["schema"]}.{self.db_info["api_params_table"]} \
                        WHERE api_name = {DataBaseUtil.convert_data(api_name)};'
                        
        api_params, column_names = db.select(params_query)
        api_params = make_res_msg("", "", api_params, column_names)

        return {"api_info" : api_info, "api_params" : api_params}
    
    def set_api_info(self, api_info:ApiInfo) -> Dict:
        db = self.connect_db()
        
        insert_api_info = {}
        insert_api_params = []
        for key, value in api_info.__dict__.items():
            if key == "params":
                for param in value:
                    insert_api_params.append(param.__dict__)
            else:
                insert_api_info[key] = value

        db.insert(self.db_info["api_info_table"], [insert_api_info])
        db.insert(self.db_info["api_params_table"], insert_api_params)
        
        return ""     

    def del_api_info(self, api_name:str) -> Dict:
        db = self.connect_db()
        
        db.delete(self.db_info["api_info_table"], {"api_name" : api_name})
        db.delete(self.db_info["api_params_table"], {"api_name" : api_name})

        return ""
    
    def route_api(self, api_name:str) -> Dict:
        # db search
        return ""
    
