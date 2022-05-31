import uuid
from typing import Dict
from fastapi.logger import logger
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_token_info
from Utils.DataBaseUtil import convert_data
from pydantic import BaseModel
from starlette.requests import Request


class InsertMetaName(BaseModel):
    KOR_NM: str
    ENG_NM: str
    TYPE: int


def api(insert: InsertMetaName, request: Request) -> Dict:
    user_info = get_token_info(request.headers)

    query = f'INSERT INTO tb_biz_meta_name ("KOR_NM", "ENG_NM", "SHOW_ODRG", "NM_ID", "TYPE")\
              VALUES ({convert_data(insert.KOR_NM)}, {convert_data(insert.ENG_NM)}, 0,\
              {convert_data(uuid.uuid4())}, {convert_data(insert.TYPE)});'
    try:
        db = connect_db(config.db_type, config.db_info)
        db.execute(query)
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        result = {"result": 1, "errorMessage": ""}
    return result
