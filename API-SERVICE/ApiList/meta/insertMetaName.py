import uuid
import string
from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_exception_info, convert_data
from pydantic import BaseModel, Field


class InsertMetaName(BaseModel):
    kor_nm: str
    eng_nm: str
    TYPE: int = Field(alias="type")


def api(insert: InsertMetaName) -> Dict:
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
        db = connect_db()
        eng_nm_list = db.select(select_eng_nm)[0]

        # 중복 체크
        if len(eng_nm_list):
            eng_nm_list = [eng_nm["eng_nm"] for eng_nm in eng_nm_list]
            if insert.eng_nm in eng_nm_list:
                raise Exception

        # 특수문자 체크
        if list(filter(lambda eng_nm: eng_nm in symbol_list, insert.eng_nm)):
            raise Exception

        db.execute(insert_meta_name)
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = {"result": 1, "errorMessage": ""}
    return result
