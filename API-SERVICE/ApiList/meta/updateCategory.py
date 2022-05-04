from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db
from Utils.DataBaseUtil import convert_data
from pydantic import BaseModel


class UpdateCategory(BaseModel):
    parent_id: str
    node_id: str
    node_name: str


# todo: 수정 필요
def api(update:UpdateCategory) -> Dict:
    db = connect_db(config.db_type, config.db_info)
    query = f'UPDATE tb_biz_meta_name\
                SET kor_name   = {convert_data(update.parent_id)},\
                    eng_name   = {convert_data(update.node_id)},\
                    show_order = {convert_data(update.node_name)}\
                WHERE name_id = {convert_data(update.node_id)};'\

    db.execute(query)
    return {"result" : "", "errorMessage" : ""}