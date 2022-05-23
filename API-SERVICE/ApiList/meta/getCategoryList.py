from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_token_info
from fastapi.logger import logger
from starlette.requests import Request


def api(request: Request) -> Dict:
    user_info = get_token_info(request.headers)

    category_query = 'select * \
                      from tb_category \
                      order by "PRNTS_ID", "NODE_ID";'

    try:
        db = connect_db(config.db_type, config.db_info)
        category_list = db.select(category_query)[0]
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        result = {"result": 1, "errorMessage": "", "data": category_list}
    return result
