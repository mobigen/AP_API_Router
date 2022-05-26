from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_token_info, make_res_msg
from fastapi.logger import logger
from starlette.requests import Request


def api(request: Request) -> Dict:
    user_info = get_token_info(request.headers)
    v_meta_wrap_query = "SELECT * FROM v_biz_meta_wrap"

    try:
        db = connect_db(config.db_type, config.db_info)
        meta_wrap = db.select(v_meta_wrap_query)
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        result = make_res_msg(1,"",meta_wrap[0],meta_wrap[1])

    return result