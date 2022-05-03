from select import select
from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db

def api() -> Dict:
    db = connect_db(config.db_type, config.db_info)

    meta_name_query = "SELECT * FROM tb_biz_meta_name;"
    meta_name = db.select(meta_name_query)

    v_meta_name_query = "SELECT * FROM v_biz_meta_name;"
    v_meta_name = db.select(v_meta_name_query)

    return {"result" : "", "errorMessage" : "", "data": {"body": meta_name[0], "header": v_meta_name[0]}}