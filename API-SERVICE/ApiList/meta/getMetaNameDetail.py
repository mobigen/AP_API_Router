from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, make_res_msg
from Utils.DataBaseUtil import convert_data
from fastapi.logger import logger


def api(nameId: str = None) -> Dict:
    if nameId is None:
        query = "SELECT * FROM v_biz_meta_name"
    else:
        query = f'SELECT * FROM tb_biz_meta_name WHERE nm_id = {convert_data(nameId)}'

    try:
        db = connect_db(config.db_info)
        meta_name = db.select(query)
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        if nameId is None:
            result = make_res_msg(1, "", {}, "")
            result["data"]["header"] = meta_name[0]
        else:
            result = make_res_msg(1, "", meta_name[0][0], meta_name[1])
    return result
