from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_token_info
from Utils.DataBaseUtil import convert_data
from pydantic import BaseModel
from fastapi.logger import logger
from starlette.requests import Request


class UpdateBizMeta(BaseModel):
    biz_dataset_id: str
    dataList: list


def api(update: UpdateBizMeta, request: Request) -> Dict:
    user_info = get_token_info(request.headers)

    try:
        db = connect_db(config.db_info)
        for data in update.dataList:
            query = f'UPDATE tb_biz_meta\
                        SET item_id   = {convert_data(data["itemId"])},\
                            item_val   = {convert_data(data["itemVal"])}\
                        WHERE biz_dataset_id = {convert_data(update.biz_dataset_id)} AND \
                            item_id = {convert_data(data["itemId"])};'

            db.execute(query)
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        result = {"result": 1, "errorMessage": ""}
    return result
