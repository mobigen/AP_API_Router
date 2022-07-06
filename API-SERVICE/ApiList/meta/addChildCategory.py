import uuid
from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_exception_info
from Utils.DataBaseUtil import convert_data
from pydantic import BaseModel


class addChildCategory(BaseModel):
    prnts_id: str
    node_nm: str


def api(insert: addChildCategory) -> Dict:
    query = f'INSERT INTO tb_category (node_nm, prnts_id, node_id)\
              VALUES ({convert_data(insert.node_nm)},{convert_data(insert.prnts_id)},{convert_data(uuid.uuid4())});'

    try:
        db = connect_db(config.db_info)
        db.execute(query)
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = {"result": 1, "errorMessage": ""}
    return result
