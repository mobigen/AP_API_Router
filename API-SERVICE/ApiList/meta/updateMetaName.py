from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_exception_info
from Utils.DataBaseUtil import convert_data
from pydantic import BaseModel, Field


class UpdatetMetaName(BaseModel):
    kor_nm: str
    eng_nm: str
    show_odrg: int
    nm_id: str
    TYPE: int = Field(alias="type")


def api(update: UpdatetMetaName) -> Dict:
    query = f'UPDATE tb_biz_meta_name\
                SET kor_nm = {convert_data(update.kor_nm)},\
                    eng_nm   = {convert_data(update.eng_nm)},\
                    show_odrg = {convert_data(update.show_odrg)},\
                    type = {convert_data(update.TYPE)}\
                WHERE nm_id = {convert_data(update.nm_id)};'

    try:
        db = connect_db()
        db.execute(query)
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = {"result": 1, "errorMessage": ""}
    return result
