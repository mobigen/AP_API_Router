import uuid
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db
from Utils.DataBaseUtil import convert_data
from pydantic import BaseModel
from fastapi.logger import logger
from typing import Dict


class UpdateCategory(BaseModel):
    node_id: str
    node_name: str


# todo: 수정 필요
def api(update: UpdateCategory) -> Dict:
    query = f'UPDATE tb_category\
                SET parent_id   = {convert_data(uuid.uuid4())},\
                    node_id   = {convert_data(update.node_id)},\
                    node_name = {convert_data(update.node_name)}\
                WHERE node_id = {convert_data(update.node_id)};'
    try:
        db = connect_db(config.db_type, config.db_info)
        db.execute(query)
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        result = {"result": 1, "errorMessage": ""}
    return result
