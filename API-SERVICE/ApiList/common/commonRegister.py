from typing import Dict
from pydantic import BaseModel
from fastapi.logger import logger
from Utils.CommonUtil import connect_db, get_exception_info
from Utils.DataBaseUtil import convert_data
from ApiService.ApiServiceConfig import config


class commonRegister(BaseModel):
    data: Dict


def make_query(register: commonRegister):
    password_column = config.user_info["password_column"]
    user_info_table = config.user_info["table"]

    columns = ", ".join(register.data.keys())
    register.data[password_column] = config.pwd_context.hash(
        register.data[password_column])
    values = ", ".join(map(convert_data, register.data.values()))
    query = f'INSERT INTO {user_info_table} ({columns}) VALUES ({values});'
    return query


def api(register: commonRegister) -> Dict:
    try:
        query = make_query(register)

        db = connect_db()
        time_zone = 'Asia/Seoul'
        db.execute(f"SET TIMEZONE={convert_data(time_zone)}")
        db.execute(query)
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = {"result": 1, "errorMessage": ""}

    return result
