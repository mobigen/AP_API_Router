from typing import Dict
from fastapi.logger import logger
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_token_info
from Utils.DataBaseUtil import convert_data
from pydantic import BaseModel
from starlette.requests import Request


class deleteUseBoardData(BaseModel):
    use_dataset_id: str


def api(use_board_data: deleteUseBoardData, request: Request) -> Dict:
    user_info = get_token_info(request.headers)
    delete_biz_meta_query = f'DELETE FROM tb_board_use WHERE use_dataset_id = {convert_data(use_board_data.use_dataset_id)};'

    try:
        db = connect_db(config.db_info)
        db.execute(delete_biz_meta_query)
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        result = {"result": 1, "errorMessage": ""}

    return result
