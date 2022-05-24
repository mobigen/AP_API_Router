from typing import Dict
from fastapi.logger import logger
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_token_info
from Utils.DataBaseUtil import convert_data
from pydantic import BaseModel, Field
from starlette.requests import Request


class InsertMetaName(BaseModel):
    subscribed: bool
    kor_name: str
    eng_name: str
    show_order: int
    name_id: str
    TYPE: int = Field(alias="type")  # 예약어 때문에 alias 처리


def api(insert: InsertMetaName, request: Request) -> Dict:
    user_info = get_token_info(request.headers)

    query = f'INSERT INTO tb_biz_meta_name ("KOR_NM", "ENG_NM", "SHOW_ODRG", "NM_ID", "TYPE")\
                VALUES ({convert_data(insert.kor_name)}, {convert_data(insert.eng_name)}, {convert_data(insert.show_order)},\
                (SELECT concat(\'i\', CAST(substring(max("NM_ID"), 2) AS INT) + 1) AS NM_ID FROM tb_biz_meta_name), {convert_data(insert.TYPE)});'
    try:
        db = connect_db(config.db_type, config.db_info)
        db.execute(query)
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        result = {"result": 1, "errorMessage": ""}
    return result
