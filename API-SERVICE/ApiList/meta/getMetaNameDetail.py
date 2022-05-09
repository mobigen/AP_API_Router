from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db
from Utils.DataBaseUtil import convert_data

def api(name_id:str) -> Dict:
    db = connect_db(config.db_type, config.db_info)

    query = f'SELECT * FROM tb_biz_meta_name WHERE name_id = {convert_data(name_id)}'

    meta_name = db.select(query)

    return {"result" : "", "errorMessage" : "", "data": meta_name[0][0]}