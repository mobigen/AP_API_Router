from typing import Dict
from ApiRoute.ApiRouteConfig import config
from Utils.CommonUtil import connect_db

def api(api_name:str) -> Dict:
    db = connect_db(config.db_type, config.db_info)

    db.delete("api_info", {"api_name" : api_name})
    db.delete("api_params", {"api_name" : api_name})
    
    return {"API_NAME" : "delApi"}