from typing import Dict, List, Optional
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_exception_info
from Utils.DataBaseUtil import convert_data
from pydantic import BaseModel


class commonMultiExcute(BaseModel):
    method: str
    table_nm: str
    data: Dict
    key: Optional[str] = None


def make_query(excute: commonMultiExcute):
    method = excute.method
    query = None
    if method == "INSERT":
        columns = ", ".join(excute.data.keys())
        values = ", ".join(map(convert_data, excute.data.values()))
        query = f'INSERT INTO {excute.table_nm} ({columns}) VALUES ({values});'
    elif method == "UPDATE":
        update_data = [
            f'{key} = {convert_data(value)}' for key, value in excute.data.items()]
        query = f'UPDATE {excute.table_nm} SET {",".join(update_data)}\
                                           WHERE {excute.key} = {convert_data(excute.data.get(excute.key))};'
    elif method == "DELETE":
        query = f'DELETE FROM {excute.table_nm} WHERE {excute.key} = {convert_data(excute.data.get(excute.key))};'
    else:
        raise ValueError(f"Invalid Method. ({method}))")
    return query


def api(excute_list: List[commonMultiExcute]) -> Dict:
    query_list = []
    try:
        for excute in excute_list:
            query_list.append(make_query(excute))

        db = connect_db(config.db_info)
        db.multiple_excute(query_list)
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = {"result": 1, "errorMessage": ""}

    return result
