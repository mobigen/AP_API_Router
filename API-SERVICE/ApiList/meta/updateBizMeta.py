from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db
from Utils.DataBaseUtil import convert_data
from pydantic import BaseModel
from fastapi.logger import logger


class UpdateBizMeta(BaseModel):
    BIZ_DATASET_ID: str
    dataList: list


def api(update: UpdateBizMeta) -> Dict:
    try:
        db = connect_db(config.db_type, config.db_info)
        for data in update.dataList:
            query = f'UPDATE tb_biz_meta\
                        SET "ITEM_ID"   = {convert_data(data["itemId"])},\
                            "ITEM_VAL"   = {convert_data(data["itemVal"])}\
                        WHERE "BIZ_DATASET_ID" = {convert_data(update.BIZ_DATASET_ID)} AND \
                            "ITEM_ID" = {convert_data(data["itemId"])};'

            db.execute(query)
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        result = {"result": 1, "errorMessage": ""}
    return result
