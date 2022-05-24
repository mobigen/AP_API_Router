import uuid
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_token_info
from Utils.DataBaseUtil import convert_data
from pydantic import BaseModel
from fastapi.logger import logger
from typing import Dict
from starlette.requests import Request


class UpdateCategory(BaseModel):
    node_id: str
    node_name: str


# todo: 수정 필요
def api(update: UpdateCategory, request: Request) -> Dict:
    user_info = get_token_info(request.headers)

    query = f'UPDATE tb_category\
                SET "PRNTS_ID"   = {convert_data(uuid.uuid4())},\
                    "NODE_ID"   = {convert_data(update.node_id)},\
                    "NODE_NM" = {convert_data(update.node_name)}\
                WHERE "NODE_ID" = {convert_data(update.node_id)};'
    try:
        db = connect_db(config.db_type, config.db_info)
        db.execute(query)
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        result = {"result": 1, "errorMessage": ""}
    return result
