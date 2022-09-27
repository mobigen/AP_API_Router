import uuid
from typing import Dict
from ServiceUtils.CommonUtil import connect_db, get_exception_info, convert_data
from pydantic import BaseModel


class addChildCategory(BaseModel):
    prnts_id: str
    node_nm: str


# todo: 수정 필요
def api(insert: addChildCategory) -> Dict:
    query = f'INSERT INTO tb_category (node_nm, prnts_id, node_id)\
              VALUES ({convert_data(insert.node_nm)},{convert_data(insert.prnts_id)},{convert_data(uuid.uuid4())});'

    try:
        db = connect_db()
        db.execute(query)
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = {"result": 1, "errorMessage": ""}
    return result
