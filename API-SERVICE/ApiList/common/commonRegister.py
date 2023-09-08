from typing import Dict
from pydantic import BaseModel
from fastapi.logger import logger
from Utils.CommonUtil import connect_db, get_exception_info, convert_data
from ApiService.ApiServiceConfig import config


class commonRegister(BaseModel):
    data: Dict


def make_register_query(register: commonRegister):
    password_column = config.user_info["password_column"]
    user_info_table = config.user_info["table"]

    # at 221109 by seokwoo-yang, password 평문 필요 요청
    register.data["user_normal"] = register.data[password_column]
    register.data[password_column] = config.pwd_context.hash(register.data[password_column])
    columns = ", ".join(register.data.keys())
    values = ", ".join(map(convert_data, register.data.values()))
    query = f"INSERT INTO {user_info_table} ({columns}) VALUES ({values});"
    return query


def api(register: commonRegister) -> Dict:
    try:
        query = make_register_query(register)

        db = connect_db()
        time_zone = "Asia/Seoul"
        db.execute(f"SET TIMEZONE={convert_data(time_zone)}")
        db.execute(query)
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = {"result": 1, "errorMessage": ""}

    return result
