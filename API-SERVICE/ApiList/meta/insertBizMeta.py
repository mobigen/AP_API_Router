import uuid
from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db
from Utils.DataBaseUtil import convert_data
from fastapi.logger import logger


def api(biz_meta_list: list) -> Dict:
    uid = uuid.uuid4()
    biz_meta_query = "SELECT ITEM_ID as itemId, ITEM_VAL as itemVal FROM tb_biz_meta;"

    try:
        db = connect_db(config.db_type, config.db_info)
        for biz_meta in biz_meta_list:
            query = f'INSERT INTO tb_biz_meta (BIZ_DATASET_ID,ITEM_ID,ITEM_VAL)\
                    VALUES ({convert_data(uid)},{convert_data(biz_meta["itemId"])},{convert_data(biz_meta["itemVal"])});'

            db.execute(query)

        biz_meta_list = db.select(biz_meta_query)[0]
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        result = biz_meta_list
    return result
