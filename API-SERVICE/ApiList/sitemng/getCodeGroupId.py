from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_token_info, make_res_msg
from fastapi.logger import logger
from starlette.requests import Request
from Utils.DataBaseUtil import convert_data


def api(groupId, request: Request) -> Dict:
    user_info = get_token_info(request.headers)

    get_code_info_query = f'select code_id, code_nm \
                            from tb_code_detail \
                            where code_group_id = {convert_data(groupId)};'

    try:
        db = connect_db(config.db_info)
        code_info = db.select(get_code_info_query)
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        result = code_info[0]
    return result