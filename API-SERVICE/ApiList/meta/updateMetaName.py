from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db
from Utils.DataBaseUtil import convert_data
from pydantic import BaseModel, Field
from fastapi.logger import logger


class UpdatetMetaName(BaseModel):
    subscribed: bool
    kor_nm: str = Field(alias="kor_name")
    eng_nm: str = Field(alias="eng_name")
    show_odrg: int = Field(alias="show_order")
    nm_id: str = Field(alias="name_id")
    type: int = Field(alias="type")


def api(update: UpdatetMetaName) -> Dict:
    query = f'UPDATE tb_biz_meta_name\
                SET "KOR_NM" = {convert_data(update.kor_nm)},\
                    "ENG_NM"   = {convert_data(update.eng_nm)},\
                    "SHOW_ODRG" = {convert_data(update.show_odrg)},\
                    "TYPE"= {convert_data(update.type)}\
                WHERE "NM_ID" = {convert_data(update.nm_id)};'

    try:
        db = connect_db(config.db_type, config.db_info)
        db.execute(query)
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        result = {"result": 1, "errorMessage": ""}
    return result
