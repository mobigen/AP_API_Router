from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_exception_info
from Utils.DataBaseUtil import convert_data
from pydantic import BaseModel


class deleteUseBoardData(BaseModel):
    use_dataset_id: str


def api(use_board_data: deleteUseBoardData) -> Dict:
    delete_biz_meta_query = f'DELETE FROM tb_board_use WHERE use_dataset_id = {convert_data(use_board_data.use_dataset_id)};'

    try:
        db = connect_db(config.db_info)
        db.execute(delete_biz_meta_query)
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = {"result": 1, "errorMessage": ""}

    return result
