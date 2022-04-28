from typing import Dict, List
from pydantic import BaseModel
from ApiRoute.ApiRouteConfig import config
from Utils.CommonUtil import connect_db
import traceback

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

def api(api_info:ApiInfo) -> Dict:
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

    return {"API_NAME" : "setApi"}