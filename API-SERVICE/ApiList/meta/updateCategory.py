import uuid
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_exception_info
from Utils.DataBaseUtil import convert_data
from pydantic import BaseModel
from typing import Dict


class UpdateCategory(BaseModel):
    node_id: str
    node_nm: str


# todo: 수정 필요
def api(update: UpdateCategory) -> Dict:
    query = f'UPDATE tb_category\
                SET prnts_id   = {convert_data(uuid.uuid4())},\
                    node_id   = {convert_data(update.node_id)},\
                    node_nm = {convert_data(update.node_nm)}\
                WHERE node_id = {convert_data(update.node_id)};'
    try:
        db = connect_db(config.db_info)
        db.execute(query)
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = {"result": 1, "errorMessage": ""}
    return result
