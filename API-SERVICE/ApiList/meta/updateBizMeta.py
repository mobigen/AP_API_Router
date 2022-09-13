from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_exception_info, convert_data
from pydantic import BaseModel


class UpdateBizMeta(BaseModel):
    biz_dataset_id: str
    dataList: list


def api(update: UpdateBizMeta) -> Dict:
    try:
        db = connect_db()
        for data in update.dataList:
            query = f'UPDATE tb_biz_meta\
                        SET item_id   = {convert_data(data["itemId"])},\
                            item_val   = {convert_data(data["itemVal"])}\
                        WHERE biz_dataset_id = {convert_data(update.biz_dataset_id)} AND \
                            item_id = {convert_data(data["itemId"])};'

            db.execute(query)
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = {"result": 1, "errorMessage": ""}
    return result
