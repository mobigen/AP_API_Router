import logging
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, List

from regex import D
from ConnectManager import PostgreManager, DataBaseUtil
import traceback


logger = logging.getLogger()

def make_res_msg(result, errorMessage, data, column_names):    
    header_list = []
    for column_name in column_names:
        header = {"column_name" : column_name} 
        header_list.append(header)          
    
    return {"result" : result, "errorMessage" : errorMessage, "body" : data, "header" : header_list}

class ApiService:
    def __init__(self, db_type:str, db_info: Dict) -> None:
        self.db_type = db_type
        self.db_info = db_info
        
        self.router = APIRouter()
        self.set_route()

    def set_route(self) -> None:
        self.router.add_api_route("/api/get_all_info", self.get_all_api_info, methods=["GET"])


    def connect_db(self):
        if self.db_type == "postgresql":
            db = PostgreManager(host=self.db_info["host"], port=self.db_info["port"],
                            user=self.db_info["user"], password=self.db_info["password"], 
                            database=self.db_info["database"], schema=self.db_info["schema"])
        else:
            logger.error(f"Not Implemented. {self.db_type}")
        return db
        

    
