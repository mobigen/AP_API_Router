import logging
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, List
from ConnectManager import RemoteCmd, PostgreManager, DataBaseUtil

logger = logging.getLogger()

class ApiParam(BaseModel):
    name: str
    data_type: str
    default: str

class ApiInfo(BaseModel):
    api_name: str
    category: str
    url: str
    msg_type: str
    method: List[str]
    protocol: str
    command: str
    params: List[ApiParam]

def make_res_msg(result):
    print("RESULT : ", result)
    return ""

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

    def get_all_api_info(self) -> Dict:
        return ""

    def get_api_info(self, api_name:str) -> Dict:
        postgres = PostgreManager(host=self.db_info["host"], port=self.db_info["port"],
                          user=self.db_info["user"], password=self.db_info["password"], 
                          database=self.db_info["database"], schema=self.db_info["schema"])
        
        info_query = f'SELECT * FROM {self.db_info["schema"]}.{self.db_info["api_info_table"]} WHERE api_name = {DataBaseUtil.convert_data(api_name)};'
        api_info = postgres.select(info_query)

        
        params_query = f'SELECT * FROM {self.db_info["schema"]}.{self.db_info["api_params_table"]} WHERE api_name = {DataBaseUtil.convert_data(api_name)};'
        api_params = postgres.select(params_query)

        return api_info
    
    def set_api_info(self, api_info:ApiInfo) -> Dict:
        return ""
    
    def del_api_info(self, api_name:str) -> Dict:
        return ""
    
    def route_api(self, api_name:str) -> Dict:
        return ""
    
