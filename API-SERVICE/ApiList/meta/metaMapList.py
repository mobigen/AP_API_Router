from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db
from fastapi.logger import logger


def api() -> Dict:
    meta_map_query = "SELECT tbmn.kor_name, tbmn.eng_name, tbmm.item_id, tbmm.name_id\
                        FROM tb_biz_meta_name tbmn\
                        JOIN tb_biz_meta_map tbmm ON tbmn.name_id = tbmm.name_id"
    v_meta_map_query = "SELECT * FROM v_biz_meta_map;"

    try:
        db = connect_db(config.db_type, config.db_info)
        meta_map = db.select(meta_map_query)
        v_meta_map = db.select(v_meta_map_query)
    except Exception as err:
        # make error response
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        # make response
        result = {"result": "", "errorMessage": "", "data": {
            "body": meta_map[0], "header": v_meta_map[0]}}
    return result
