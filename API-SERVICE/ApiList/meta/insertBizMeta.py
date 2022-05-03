from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db
from Utils.DataBaseUtil import convert_data

'''
'''
def api() -> Dict:
    db = connect_db(config.db_type, config.db_info)

    return {"API_NAME" : "TEST"}