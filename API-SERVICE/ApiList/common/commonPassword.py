from typing import Dict, Optional
from pydantic import BaseModel
from fastapi.logger import logger
from Utils.CommonUtil import connect_db, get_exception_info, convert_data, authenticate_user
from ApiService.ApiServiceConfig import config


class commonPassword(BaseModel):
    data: Dict
    new_password: Optional[str] = ""


def api(password: commonPassword) -> Dict:
    user_id = password.data.get(config.user_info["id_column"])
    cur_password = password.data.get(config.user_info["password_column"])
    new_password = password.new_password
    user_info_table = config.user_info["table"]
    try:
        db = connect_db()
        authenticate_user(user_id, cur_password)
        if new_password:
            logger.info("Change Password")
            time_zone = 'Asia/Seoul'
            db.execute(f"SET TIMEZONE={convert_data(time_zone)}")
            db.execute(
                f'UPDATE {user_info_table} SET {config.user_info["password_column"]} = {convert_data(config.pwd_context.hash(new_password))},'
                f' {config.user_info["normal_password"]} = {convert_data(new_password)} WHERE {config.user_info["id_column"]} = {convert_data(user_id)};')
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = {"result": 1, "errorMessage": ""}

    return result
