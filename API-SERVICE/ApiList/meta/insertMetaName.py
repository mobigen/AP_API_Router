from typing import Dict
from fastapi.logger import logger
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db
from Utils.DataBaseUtil import convert_data
from pydantic import BaseModel, Field


class InsertMetaName(BaseModel):
    subscribed: bool
    kor_nm: str = Field(alias="kor_name")
    eng_nm: str = Field(alias="eng_name")
    show_odrg: int = Field(alias="show_order")
    nm_id: str = Field(alias="name_id")
    type: int = Field(alias="type")


def api(insert: InsertMetaName) -> Dict:
    query = f'INSERT INTO tb_biz_meta_name ("KOR_NM", "ENG_NM", "SHOW_ODRG", "NM_ID", "TYPE")\
                VALUES ({convert_data(insert.kor_nm)}, {convert_data(insert.eng_nm)}, {convert_data(insert.show_odrg)},\
                (SELECT concat(\'i\', CAST(substring(max("NM_ID"), 2) AS INT) + 1) AS name_id FROM tb_biz_meta_name), {convert_data(insert.type)});'
    try:
        db = connect_db(config.db_type, config.db_info)
        db.execute(query)
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        result = {"result": 1, "errorMessage": ""}
    return result
