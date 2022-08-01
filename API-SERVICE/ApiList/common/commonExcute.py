from typing import Dict, List, Optional
from pydantic import BaseModel
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_exception_info
from Utils.DataBaseUtil import convert_data


class commonExcute(BaseModel):
    method: str
    table_nm: str
    data: Dict
    key: Optional[List[str]] = None


def make_query(excute: commonExcute):
    method = excute.method
    where = []
    query = None
    if method == "INSERT":
        columns = ", ".join(excute.data.keys())
        values = ", ".join(map(convert_data, excute.data.values()))
        query = f'INSERT INTO {excute.table_nm} ({columns}) VALUES ({values});'
    elif method == "UPDATE":
        update_data = [
            f'{key} = {convert_data(value)}' for key, value in excute.data.items()]
        for key in excute.key:
            where.append(f'{key} = {convert_data(excute.data.get(key))}')
        query = f'UPDATE {excute.table_nm} SET {",".join(update_data)}\
                                           WHERE {" AND ".join(where)};'
    elif method == "DELETE":
        for key in excute.key:
            where.append(f'{key} = {convert_data(excute.data.get(key))}')
        query = f'DELETE FROM {excute.table_nm} WHERE {" AND ".join(where)};'
    else:
        raise ValueError(f"Invalid Method. ({method}))")
    return query


def api(excute_list: List[commonExcute]) -> Dict:
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
