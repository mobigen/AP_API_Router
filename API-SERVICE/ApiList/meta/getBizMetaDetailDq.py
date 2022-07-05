from fastapi.logger import logger
from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, make_res_msg
from Utils.DataBaseUtil import convert_data
from starlette.requests import Request


def api(request: Request, datasetId: str = None) -> Dict:
    v_meta_dq_query = f'SELECT * FROM tb_meta_detail_dq WHERE biz_dataset_id = {convert_data(datasetId)}'

    try:
        db = connect_db(config.db_info)
        meta_dq = db.select(v_meta_dq_query)
        logger.error(meta_dq)
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)

    else:
        result = make_res_msg(1, "", meta_dq[0], meta_dq[1])

    return result
