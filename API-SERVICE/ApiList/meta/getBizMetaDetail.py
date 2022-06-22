from fastapi.logger import logger
from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_token_info, make_res_msg
from Utils.DataBaseUtil import convert_data
from starlette.requests import Request


def api(request: Request, datasetId: str = None) -> Dict:
    user_info = get_token_info(request.headers)

    if datasetId is None:
        v_meta_wrap_query = f'SELECT * FROM v_biz_meta_wrap LIMIT 1;'
    else:
        v_meta_wrap_query = f'SELECT * FROM v_biz_meta_wrap WHERE biz_dataset_id = {convert_data(datasetId)}'

    try:
        db = connect_db(config.db_info)
        meta_wrap = db.select(v_meta_wrap_query)
        # v_meta_name = db.select(v_meta_name_query)
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        if datasetId is None:
            result = make_res_msg(1, "", {}, meta_wrap[1])
        else:
            kor_nm_list = []
            name_list, _ = db.select(f'SELECT eng_nm, kor_nm FROM v_biz_meta;')
            name_info = {}
            for name in name_list:
                name_info[name['eng_nm']] = name['kor_nm']
            for eng_nm in meta_wrap[1]:
                if eng_nm in name_info:
                    kor_nm_list.append(name_info[eng_nm])
                else:
                    kor_nm_list.append("")
            result = make_res_msg(
                1, "", meta_wrap[0][0], meta_wrap[1], kor_nm_list)
    return result
