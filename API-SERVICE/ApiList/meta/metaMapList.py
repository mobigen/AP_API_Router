from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, make_res_msg
from fastapi.logger import logger


def api() -> Dict:
    meta_map_query = "SELECT\
                          tbmn.kor_nm,\
                          tbmn.eng_nm,\
                          tbmm.item_id,\
                          tbmm.nm_id\
                      FROM\
                          tb_biz_meta_name AS tbmn\
                      JOIN tb_biz_meta_map AS tbmm\
                      ON tbmm.nm_id = tbmn.nm_id;"

    try:
        db = connect_db(config.db_info)
        meta_map = db.select(meta_map_query)
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        result = make_res_msg(1, "",  meta_map[0],  meta_map[1])
    return result
