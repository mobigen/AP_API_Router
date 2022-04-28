from typing import Dict
from ApiRoute.ApiRouteInfo import config
from Utils.CommonUtil import connect_db

def api() -> Dict:
    '''
        db = self.connect_db()
        
        info_query = f'SELECT * FROM {self.db_info["schema"]}.{self.db_info["api_info_table"]};'
        api_info, column_names = db.select(info_query)
        api_info = make_res_msg("", "", api_info, column_names)
        
        params_query = f'SELECT * FROM {self.db_info["schema"]}.{self.db_info["api_params_table"]};'
        api_params, column_names = db.select(params_query)
        api_params = make_res_msg("", "", api_params, column_names)
        
        return {"api_info" : api_info, "api_params" : api_params}
    '''
    return {"API_NAME" : "getApiList"}