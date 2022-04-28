from typing import Dict
from ApiRoute.ApiRouteConfig import config
from Utils.CommonUtil import connect_db, make_res_msg
from Utils.DataBaseUtil import convert_data

def api(api_name:str) -> Dict:
    db = connect_db(config.db_type, config.db_info)
    
    api_info_query = f'SELECT * FROM api_info WHERE api_name = {convert_data(api_name)};'
                    
    api_info, column_names = db.select(api_info_query)
    api_info = make_res_msg("", "", api_info, column_names)
    
    api_params_query = f'SELECT * FROM api_params WHERE api_name = {convert_data(api_name)};'
                    
    api_params, column_names = db.select(api_params_query)
    api_params = make_res_msg("", "", api_params, column_names)

    return {"api_info" : api_info, "api_params" : api_params}
