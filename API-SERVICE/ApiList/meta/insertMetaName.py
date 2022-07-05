import uuid
import string
from typing import Dict
from fastapi.logger import logger
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_token_info
from Utils.DataBaseUtil import convert_data
from pydantic import BaseModel, Field
from starlette.requests import Request


class InsertMetaName(BaseModel):
    kor_nm: str
    eng_nm: str
    TYPE: int = Field(alias="type")


def api(insert: InsertMetaName, request: Request) -> Dict:
    user_info = get_token_info(request.headers)

    insert_meta_name = f'INSERT INTO tb_biz_meta_name (kor_nm, eng_nm, show_odrg, nm_id, type)\
              VALUES ({convert_data(insert.kor_nm)}, {convert_data(insert.eng_nm.lower())}, 0,\
                      {convert_data(uuid.uuid4())}, {convert_data(insert.TYPE)});'
    symbol_list = list(map(str, string.punctuation))
    symbol_list.remove("_")
    symbol_list.remove("'")
    symbol_list.remove('"')
    symbol_list.remove("-")
    select_eng_nm = 'SELECT eng_nm FROM tb_biz_meta_name'
    try:
        db = connect_db(config.db_info)
        eng_nm_list = db.select(select_eng_nm)[0]
        logger.info(eng_nm_list)

        # 중복 체크
        if len(eng_nm_list):
            eng_nm_list = [eng_nm["eng_nm"] for eng_nm in eng_nm_list]
            if insert.eng_nm in eng_nm_list:
                raise ValueError

        # 특수문자 체크
        if list(filter(lambda eng_nm: eng_nm in symbol_list, insert.eng_nm)):
            raise ValueError

        db.execute(insert_meta_name)
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    except ValueError as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        result = {"result": 1, "errorMessage": ""}
    return result
