from typing import Dict
from pydantic import BaseModel
from fastapi.logger import logger
from passlib.context import CryptContext
from Utils.CommonUtil import connect_db, get_exception_info
from Utils.DataBaseUtil import convert_data
from ApiService.ApiServiceConfig import config

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class commonRegister(BaseModel):
    data: Dict


def make_query(register: commonRegister):
    columns = ", ".join(register.data.keys())
    register.data[config.user_info["pass_key"]] = pwd_context.hash(
        register.data[config.user_info["pass_key"]])
    values = ", ".join(map(convert_data, register.data.values()))
    query = f'INSERT INTO {config.user_info["table"]} ({columns}) VALUES ({values});'
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
