from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db
from Utils.DataBaseUtil import convert_data
from fastapi.logger import logger


def api(nameId: str) -> Dict:
    query = f'SELECT * FROM tb_biz_meta_name WHERE name_id = {convert_data(nameId)}'

    try:
        db = connect_db(config.db_type, config.db_info)
        meta_name = db.select(query)
    except Exception as err:
        # make error response
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        # make response
        result = {"result": "", "errorMessage": "", "data": meta_name[0][0]}
    return result
