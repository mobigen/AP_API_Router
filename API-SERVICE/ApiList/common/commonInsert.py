from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, make_res_msg, get_exception_info
from Utils.DataBaseUtil import convert_data
from pydantic import BaseModel


class commonInsert(BaseModel):
    table_nm: str
    data: Dict


def api(common: commonInsert) -> Dict:
    columns = ", ".join(common.data.keys())
    values = ", ".join(map(convert_data, common.data.values()))
    insert_query = f'INSERT INTO {common.table_nm} ({columns}) VALUES ({values});'

    try:
        db = connect_db(config.db_info)
        db.execute(insert_query)
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = {"result": 1, "errorMessage": ""}

    return result
