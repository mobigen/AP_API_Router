from typing import Dict
from fastapi.logger import logger
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db
from Utils.DataBaseUtil import convert_data
from pydantic import BaseModel, Field


class InsertMetaName(BaseModel):
    subscribed: bool
    KOR_NM: str = Field(alias="kor_name")
    ENG_NM: str = Field(alias="eng_name")
    SHOW_ODRG: int = Field(alias="show_order")
    NM_ID: str = Field(alias="name_id")
    TYPE: int = Field(alias="type")


def api(insert: InsertMetaName) -> Dict:
    query = f'INSERT INTO tb_biz_meta_name (KOR_NM, ENG_NM, SHOW_ODRG, NM_ID, TYPE)\
                VALUES ({convert_data(insert.KOR_NM)}, {convert_data(insert.ENG_NM)}, {convert_data(insert.SHOW_ODRG)},\
                (SELECT concat(\'i\', CAST(substring(max(NM_ID), 2) AS INT) + 1) AS name_id FROM tb_biz_meta_name), {convert_data(insert.TYPE)});'
    try:
        db = connect_db(config.db_type, config.db_info)
        db.execute(query)
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        result = {"result": 1, "errorMessage": ""}
    return result
