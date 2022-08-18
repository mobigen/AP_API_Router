from typing import Dict, List
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_exception_info
from Utils.DataBaseUtil import convert_data
from pydantic import BaseModel


class commonMultiInsert(BaseModel):
    table_nm: str
    data: Dict


def api(common_list: List[commonMultiInsert]) -> Dict:
    insert_query_list = []
    for common in common_list:
        columns = ", ".join(common.data.keys())
        values = ", ".join(map(convert_data, common.data.values()))
        insert_query_list.append(
            f'INSERT INTO {common.table_nm} ({columns}) VALUES ({values});')

    try:
        db = connect_db()
        db.multiple_excute(insert_query_list)
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = {"result": 1, "errorMessage": ""}

    return result
