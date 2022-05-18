import uuid
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db
from Utils.DataBaseUtil import convert_data
from pydantic import BaseModel, Field
from fastapi.logger import logger
from typing import Dict


class UpdateCategory(BaseModel):
    NODE_ID: str = Field(alias="NODE_ID")
    NODE_NAME: str = Field(alias="NODE_NAME")


# todo: 수정 필요
def api(update: UpdateCategory) -> Dict:
    query = f'UPDATE tb_category\
                SET PRNTS_ID   = {convert_data(uuid.uuid4())},\
                    NODE_ID   = {convert_data(update.NODE_ID)},\
                    NODE_NAME = {convert_data(update.NODE_NAME)}\
                WHERE NODE_ID = {convert_data(update.NODE_ID)};'
    try:
        db = connect_db(config.db_type, config.db_info)
        db.execute(query)
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        result = {"result": 1, "errorMessage": ""}
    return result
