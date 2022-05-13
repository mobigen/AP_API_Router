from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db
from Utils.DataBaseUtil import convert_data
from pydantic import BaseModel
from fastapi.logger import logger


class UpdateBizMeta(BaseModel):
    bizDatasetId: str
    dataList: list

# todo: 질문 후 수정 필요


def api(update: UpdateBizMeta) -> Dict:
    try:
        db = connect_db(config.db_type, config.db_info)
        for data in update.dataList:
            query = f'UPDATE tb_biz_meta\
                        SET item_id   = {convert_data(data["itemId"])},\
                            item_val   = {convert_data(data["itemVal"])}\
                        WHERE biz_dataset_id = {convert_data(update.bizDatasetId)} AND \
                            item_id = {convert_data(data["itemId"])};'

            db.execute(query)
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        result = {"result": 1, "errorMessage": ""}
    return result
