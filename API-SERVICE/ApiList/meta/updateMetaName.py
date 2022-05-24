from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_token_info
from Utils.DataBaseUtil import convert_data
from pydantic import BaseModel, Field
from fastapi.logger import logger
from starlette.requests import Request


class UpdatetMetaName(BaseModel):
    subscribed: bool
    kor_name: str
    eng_name: str
    show_order: int
    name_id: str
    TYPE: int = Field(alias="type")


def api(update: UpdatetMetaName, request: Request) -> Dict:
    user_info = get_token_info(request.headers)

    query = f'UPDATE tb_biz_meta_name\
                SET "KOR_NM" = {convert_data(update.kor_name)},\
                    "ENG_NM"   = {convert_data(update.eng_name)},\
                    "SHOW_ODRG" = {convert_data(update.show_order)},\
                    "TYPE"= {convert_data(update.TYPE)}\
                WHERE "NM_ID" = {convert_data(update.name_id)};'

    try:
        db = connect_db(config.db_type, config.db_info)
        db.execute(query)
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        result = {"result": 1, "errorMessage": ""}
    return result
