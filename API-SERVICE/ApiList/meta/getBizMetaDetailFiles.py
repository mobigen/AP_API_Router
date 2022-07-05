from fastapi.logger import logger
from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_token_info, make_res_msg
from Utils.DataBaseUtil import convert_data
from starlette.requests import Request


def api(request: Request, datasetId: str = None) -> Dict:
    user_info = get_token_info(request.headers)
    v_meta_files_query = f'SELECT * FROM tb_meta_detail_files WHERE biz_dataset_id = {convert_data(datasetId)}'

    try:
        db = connect_db(config.db_info)
        meta_files = db.select(v_meta_files_query)
        logger.error(meta_files)
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)

    else:
        result = make_res_msg(1, "", meta_files[0], meta_files[1])

    return result
