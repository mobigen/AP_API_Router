from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db
from Utils.DataBaseUtil import convert_data
from pydantic import BaseModel
from fastapi.logger import logger


class UpdatetMetaName(BaseModel):
    subscribed: bool
    kor_name: str
    eng_name: str
    show_order: int
    name_id: str
    type: int


def api(update: UpdatetMetaName) -> Dict:
    db = connect_db(config.db_type, config.db_info)
    query = f'UPDATE tb_biz_meta_name\
                SET kor_name   = {convert_data(update.kor_name)},\
                    eng_name   = {convert_data(update.eng_name)},\
                    show_order = {convert_data(update.show_order)},\
                    type= {convert_data(update.type)}\
                WHERE name_id = {convert_data(update.name_id)};'\

    db.execute(query)
    return {"result": "", "errorMessage": ""}
