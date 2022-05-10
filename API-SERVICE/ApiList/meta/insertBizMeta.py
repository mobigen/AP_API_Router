import uuid
from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db
from Utils.DataBaseUtil import convert_data
from fastapi.logger import logger


def api(biz_meta_list: list) -> Dict:
    uid = uuid.uuid4()
    biz_meta_query = "SELECT item_id as itemId, item_val as itemVal FROM tb_biz_meta;"

    try:
        db = connect_db(config.db_type, config.db_info)
        for biz_meta in biz_meta_list:
            query = f'INSERT INTO tb_biz_meta (biz_dataset_id,item_id,item_val)\
                    VALUES ({convert_data(uid)},{convert_data(biz_meta["itemId"])},{convert_data(biz_meta["itemVal"])});'

            db.execute(query)

        biz_meta_list = db.select(biz_meta_query)[0]
    except Exception as err:
        # make error response
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        # make response
        result = biz_meta_list
    return result
