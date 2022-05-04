from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db
from Utils.DataBaseUtil import convert_data


def api() -> Dict:
    db = connect_db(config.db_type, config.db_info)
    meta_name_query = "SELECT * FROM tb_biz_meta_name;"
    meta_name = db.select(meta_name_query)

    return {"result" : "", "errorMessage" : "", "data": {"body": meta_name[0]}}