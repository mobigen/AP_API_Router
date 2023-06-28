from typing import Dict
from pydantic import BaseModel
from fastapi.logger import logger
from Utils.CommonUtil import connect_db, get_admin_token, get_exception_info, convert_data, get_keycloak_manager
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


async def api(register: commonRegister) -> Dict:
    try:
        admin_token = await get_admin_token()

        reg_data = {
            "username": register.data["user_id"],
            "firstName": register.data["user_nm"],
            "email": register.data["email"],
            "emailVerified": True,
            "enabled": True,
            "credentials": [{"value": register.data["user_password"]}],
            "attributes": register.data,
        }
        print(config.keycloak_info["realm"])
        res = await get_keycloak_manager().create_user(
            token=admin_token, realm=config.keycloak_info["realm"], **reg_data
        )
        print(res)

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
