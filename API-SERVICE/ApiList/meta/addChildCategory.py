import uuid
from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db
from Utils.DataBaseUtil import convert_data
from pydantic import BaseModel, Field
from fastapi.logger import logger


class addChildCategory(BaseModel):
    PRNTS_ID: str = Field(alias="parent_id")
    NODE_NAME: str = Field(alias="node_name")


# todo: 수정 필요
def api(insert: addChildCategory) -> Dict:
    query = f'INSERT INTO tb_category (NODE_NAME, PRNTS_ID, NODE_ID)\
              VALUES ({convert_data(insert.NODE_NAME)},{convert_data(insert.PRNTS_ID)},{convert_data(uuid.uuid4())});'

    try:
        db = connect_db(config.db_type, config.db_info)
        db.execute(query)
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        # make response
        result = {"result": 1, "errorMessage": ""}
    return result
