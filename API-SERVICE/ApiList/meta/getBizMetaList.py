from lib2to3.pytree import convert
from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_token_info, make_res_msg
from Utils.DataBaseUtil import convert_data
from fastapi.logger import logger
from starlette.requests import Request


def api(request: Request) -> Dict:
    user_info = get_token_info(request.headers)
    v_meta_wrap_query = "SELECT * FROM v_biz_meta_wrap"

    try:
        db = connect_db(config.db_info)
        meta_wrap = db.select(v_meta_wrap_query)
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        kor_nm_list = []
        name_list, _ = db.select(
            f'SELECT eng_nm, kor_nm FROM v_biz_meta;')
        name_info = {}
        for name in name_list:
            name_info[name['eng_nm']] = name['kor_nm']
        for eng_nm in meta_wrap[1]:
            if eng_nm in name_info:
                kor_nm_list.append(name_info[eng_nm])
            else:
                kor_nm_list.append("")
        result = make_res_msg(
            1, "", meta_wrap[0], meta_wrap[1], kor_nm_list)

    return result
