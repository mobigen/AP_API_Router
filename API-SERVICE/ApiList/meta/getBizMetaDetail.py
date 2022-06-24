from fastapi.logger import logger
from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_token_info, make_res_msg
from Utils.DataBaseUtil import convert_data
from starlette.requests import Request


def api(request: Request, datasetId: str = None) -> Dict:
    user_info = get_token_info(request.headers)
    body = dict()
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
        name_map = {name_map["eng_nm"]: name_map["kor_nm"] for name_map in meta_map[0]}

        for meta_data in meta_wrap[0]:
            body["kor_name"] = list(name_map.values())
            body["data"] = list(meta_data.values())
            body["eng_name"] = list(name_map.keys())
            body["type"] = [0 for i in range(0,len(meta_map[0]))]
            body["columnkey"] = list(meta_data.keys())
            body["biz_dataset_id"] = datasetId

        result = make_res_msg(1,"",body,meta_map[0])

    return result
