import logging

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, List

import re
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
    def __init__(self, db_type:str, db_info: Dict, query_info: Dict) -> None:
        self.db_type = db_type
        self.db_info = db_info
        self.query_info = query_info
        
        self.router = APIRouter()
        self.set_route()

    def set_route(self) -> None:
        self.router.add_api_route("/api/meta/metaNameList", self.get_biz_meta_name_list, methods=["GET"])
        self.router.add_api_route("/api/meta/getMetaName", self.get_meta_name_detail, methods=["GET"])
        #self.router.add_api_route("/api/meta/insertMetaName", self., methods=["POST"])
        #self.router.add_api_route("/api/meta/updateMetaName", self., methods=["PUT"])
        self.router.add_api_route("/api/meta/metaMapList", self.get_meta_map_list, methods=["GET"])
        self.router.add_api_route("/api/meta/useMetaNameList", self.get_use_meta_name_list, methods=["GET"])
        #self.router.add_api_route("/api/meta/insertMetaMap", self., methods=["POST"])
        self.router.add_api_route("/api/meta/getBizMetaList", self.get_biz_meta_list, methods=["GET"])
        self.router.add_api_route("/api/meta/getBizMetaDetail", self.get_biz_meta_detail, methods=["GET"])
        #self.router.add_api_route("/api/meta/insertBizMeta", self., methods=["POST"])
        #self.router.add_api_route("/api/meta/updateBizMeta", self., methods=["PUT"])
        self.router.add_api_route("/api/meta/getCategoryList", self.get_categor_list, methods=["GET"])
        #self.router.add_api_route("/api/meta/updateCategory", self., methods=["PUT", "POST"])

    def connect_db(self):
        if self.db_type == "postgresql":
            db = PostgreManager(host=self.db_info["host"], port=self.db_info["port"],
                            user=self.db_info["user"], password=self.db_info["password"], 
                            database=self.db_info["database"], schema=self.db_info["schema"])
        else:
            logger.error(f"Not Implemented. {self.db_type}")
        return db
        
    def get_biz_meta_name_list(self):
        db = self.connect_db()

        body_query = f'SELECT * FROM {self.db_info["biz_meta_name_table"]};'
        body_info, _ = db.select(body_query)
        
        header_query = f'SELECT * FROM {self.db_info["biz_meta_name_table"].replace("tb", "v")};'
        header_info, _ = db.select(header_query)

        return {"result" : "", "errorMessage" : "", "data" : {"body" : body_info, "header" : header_info}}
    
    def get_meta_name_detail(self, name_id:str):
        db = self.connect_db()
        query = re.sub(f'#name_id#', DataBaseUtil.convert_data(name_id), self.query_info["getMetaNameDetail"])
        
        data, _ = db.select(query)

        return {"result" : "", "errorMessage" : "", "data" : data[0]}

    def get_meta_map_list(self):
        db = self.connect_db()
        
        body_info, _ = db.select(self.query_info["getMetaMapList"])
        
        header_query = f'SELECT * FROM {self.db_info["biz_meta_map_table"].replace("tb", "v")};'
        header_info, _ = db.select(header_query)

        return {"result" : "", "errorMessage" : "", "data" : {"body" : body_info, "header" : header_info}}
    
    def get_use_meta_name_list(self):
        db = self.connect_db()
        
        data, _ = db.select(self.query_info["getUseMetaNameList"])

        return {"result" : "", "errorMessage" : "", "data" : data}

    def get_biz_meta_list(self):
        db = self.connect_db()
        
        body_info, _ = db.select(self.query_info["getBizMetaList"])
        header_info, _ = db.select(f'SELECT * FROM v_biz_meta;')

        return {"result" : "", "errorMessage" : "", "data" : {"body" : body_info, "header" : header_info}}

    def get_biz_meta_detail(self, data_base_id:str):
        return ""
    
    def get_categor_list(self):
        db = self.connect_db()
        data, _ = db.select(self.query_info["getCategoryList"])
        return {"result" : "", "errorMessage" : "", "data" : data}
