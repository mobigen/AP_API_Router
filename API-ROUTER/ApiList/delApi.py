from typing import Dict
from ApiRoute.ApiRouteInfo import config
from Utils.CommonUtil import connect_db

def api(api_name:str) -> Dict:
    db = connect_db(config.db_type, config.db_info)

    db.delete(config.db_info["api_info_table"], {"api_name" : api_name})
    db.delete(config.db_info["api_params_table"], {"api_name" : api_name})
    
    return {"API_NAME" : "delApi"}