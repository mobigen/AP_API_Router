from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_exception_info
from Utils.DataBaseUtil import convert_data
from pydantic import BaseModel


class commonUpdate(BaseModel):
    table_nm: str
    key: str
    data: Dict


def api(common: commonUpdate) -> Dict:
    update_data = [
        f'{key} = {convert_data(value)}' for key, value in common.data.items()]
    update_query = f'UPDATE {common.table_nm} SET {",".join(update_data)}\
                                              WHERE {common.key} = {convert_data(common.data.get(common.key))};'

    try:
        db = connect_db()
        db.execute(update_query)
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = {"result": 1, "errorMessage": ""}

    return result
