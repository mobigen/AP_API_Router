from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db
from Utils.DataBaseUtil import convert_data
from pydantic import BaseModel


class UpdateBizMeta(BaseModel):
    bizDatasetId: str
    dataList: list

# todo: 질문 후 수정 필요
def api(update: UpdateBizMeta) -> Dict:
    db = connect_db(config.db_type, config.db_info)
    for data in update.dataList:
        query = f'UPDATE lum_test\
                    SET item_id   = {convert_data(data["itemId"])},\
                        item_val   = {convert_data(data["itemVal"])}\
                    WHERE biz_dataset_id = {convert_data(update.bizDatasetId)} AND \
                          item_id = {convert_data(update.data["itemId"])};'

        db.execute(query)
    return {"result" : "", "errorMessage" : ""}