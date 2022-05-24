import uuid
from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_token_info
from Utils.DataBaseUtil import convert_data
from pydantic import BaseModel
from fastapi.logger import logger
from starlette.requests import Request


class addChildCategory(BaseModel):
    parent_id: str
    node_name: str


# todo: 수정 필요
def api(insert: addChildCategory, request: Request) -> Dict:
    user_info = get_token_info(request.headers)

    query = f'INSERT INTO tb_category ("NODE_NM", "PRNTS_ID", "NODE_ID")\
              VALUES ({convert_data(insert.node_name)},{convert_data(insert.parent_id)},{convert_data(uuid.uuid4())});'

    try:
        db = connect_db(config.db_type, config.db_info)
        db.execute(query)
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        result = {"result": 1, "errorMessage": ""}
    return result
