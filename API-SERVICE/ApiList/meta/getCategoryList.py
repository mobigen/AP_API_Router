from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db
from fastapi.logger import logger


def api() -> Dict:
    category_query = "select * \
                      from meta.tb_category \
                      order by parent_id, node_id;"

    try:
        db = connect_db(config.db_type, config.db_info)
        category_list = db.select(category_query)[0]
    except Exception as err:
        # make error response
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        # make response
        result = {"result": "", "errorMessage": "", "data": category_list}
    return result
