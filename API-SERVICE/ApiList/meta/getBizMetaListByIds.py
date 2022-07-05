from fastapi.logger import logger
from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_token_info, make_res_msg
from Utils.DataBaseUtil import convert_data
from starlette.requests import Request


def api(request: Request, datasetIdList: str) -> Dict:
    user_info = get_token_info(request.headers)
    v_meta_wrap_query = 'SELECT * FROM v_biz_meta_wrap WHERE biz_dataset_id in ({0})'

    try:
        db = connect_db(config.db_info)
        dataset_id_list = ','.join(
            [convert_data(biz_dataset_id) for biz_dataset_id in datasetIdList.split(",")]
        )
        meta_wrap = db.select(v_meta_wrap_query.format(dataset_id_list))

    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)

    else:
        result = make_res_msg(1,"",meta_wrap[0],[])
        result["data"].pop("header")
        result["data"]["list"] = result["data"]["body"]
        del result["data"]["body"]
        logger.info(result)

    return result