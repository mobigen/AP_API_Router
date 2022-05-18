from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db
from Utils.DataBaseUtil import convert_data
from pydantic import BaseModel, Field
from fastapi.logger import logger


class UpdatetMetaName(BaseModel):
    subscribed: bool
    KOR_NM: str = Field(alias="kor_name")
    ENG_NM: str = Field(alias="eng_name")
    SHOW_ODRG: int = Field(alias="show_order")
    NM_ID: str = Field(alias="name_id")
    TYPE: int = Field(alias="type")


def api(update: UpdatetMetaName) -> Dict:
    query = f'UPDATE tb_biz_meta_name\
                SET KOR_NM = {convert_data(update.KOR_NM)},\
                    ENG_NM   = {convert_data(update.ENG_NM)},\
                    SHOW_ODRG = {convert_data(update.SHOW_ODRG)},\
                    TYPE= {convert_data(update.TYPE)}\
                WHERE NM_ID = {convert_data(update.NM_ID)};'\

    try:
        db = connect_db(config.db_type, config.db_info)
        db.execute(query)
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        result = {"result": 1, "errorMessage": ""}
    return result
