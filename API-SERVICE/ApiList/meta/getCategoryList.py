from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db
from fastapi.logger import logger


def api() -> Dict:
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
