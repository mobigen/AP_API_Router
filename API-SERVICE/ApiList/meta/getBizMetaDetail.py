from fastapi.logger import logger
from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_token_info, make_res_msg
from Utils.DataBaseUtil import convert_data
from starlette.requests import Request


def api(request: Request, datasetId: str = None) -> Dict:
    user_info = get_token_info(reques정.headers)
    v_meta_map_query = 'SELECT kor_nm,eng_nm,nm_id FROM v_biz_meta'
    v_meta_wrap_query = f'SELECT * FROM v_biz_meta_wrap WHERE biz_dataset_id = {convert_data(datasetId)}'

    try:
        db = connect_db(config.db_info)
        meta_wrap = db.select(v_meta_wrap_query)
        meta_map = db.select(v_meta_map_query)

    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)

    else:
        kor_nm_list = [map_data["kor_nm"] for map_data in meta_map[0]]
        eng_nm_list = [map_data["eng_nm"] for map_data in meta_map[0]]
        result = make_res_msg(1,"",meta_wrap[0][0],eng_nm_list,kor_nm_list)

    return result
