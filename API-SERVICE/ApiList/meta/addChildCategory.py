from tkinter import E
import uuid
from typing import Dict, Optional
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db
from Utils.DataBaseUtil import convert_data
from pydantic import BaseModel
from fastapi.logger import logger


class addChildCategory(BaseModel):
    parent_id: str
    node_name: str


# todo: 수정 필요
def api(insert: addChildCategory) -> Dict:
    query = f'INSERT INTO tb_category (node_name, parent_id, node_id)\
              VALUES ({convert_data(insert.node_name)},{convert_data(insert.parent_id)},{convert_data(uuid.uuid4())});'

    try:
        db = connect_db(config.db_type, config.db_info)
        db.execute(query)
    except Exception as err:
        # make error response
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        # make response
        result = {"result": 1, "errorMessage": ""}
    return result
