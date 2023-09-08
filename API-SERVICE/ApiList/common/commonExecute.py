from typing import Dict, List, Optional
from pydantic import BaseModel
from Utils.CommonUtil import connect_db, get_exception_info, convert_data


class commonExecute(BaseModel):
    method: str
    table_nm: str
    data: Dict
    key: Optional[List[str]] = None


def make_insert_query(excute: commonExecute):
    columns = ", ".join(excute.data.keys())
    values = ", ".join(map(convert_data, excute.data.values()))
    return f"INSERT INTO {excute.table_nm} ({columns}) VALUES ({values});"


def make_update_query(excute: commonExecute):
    where = []
    update_data = [
        f"{key} = {convert_data(value)}" for key, value in excute.data.items()
    ]
    for key in excute.key:
        where.append(f"{key} = {convert_data(excute.data.get(key))}")
    return f'UPDATE {excute.table_nm} SET {",".join(update_data)}\
                                        WHERE {" AND ".join(where)};'


def make_delete_query(excute: commonExecute):
    where = []
    for key in excute.key:
        where.append(f"{key} = {convert_data(excute.data.get(key))}")
    return f'DELETE FROM {excute.table_nm} WHERE {" AND ".join(where)};'


def make_execute_query(excute: commonExecute):
    method = excute.method
    query = None
    if method == "INSERT":
        query = make_insert_query(excute)
    elif method == "UPDATE":
        query = make_update_query(excute)
    elif method == "DELETE":
        query = make_delete_query(excute)
    else:
        raise ValueError(f"Invalid Method. ({method}))")
    return query


def api(excute_list: List[commonExecute]) -> Dict:
    query_list = []
    try:
        for excute in excute_list:
            query_list.append(make_execute_query(excute))

        db = connect_db()
        time_zone = "Asia/Seoul"
        db.execute(f"SET TIMEZONE={convert_data(time_zone)}")
        db.multiple_excute(query_list)
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = {"result": 1, "errorMessage": ""}

    return result
