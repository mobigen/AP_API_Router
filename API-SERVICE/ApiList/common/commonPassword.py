from typing import Dict, Optional
from pydantic import BaseModel
from fastapi.logger import logger
from fastapi.requests import Request
from jose import jwt
from Utils.CommonUtil import (
    connect_db,
    get_exception_info,
    convert_data,
    authenticate_user,
)
from ApiService.ApiServiceConfig import config
from Utils.exceptions import InvalidUserInfo, TokenDoesNotExist


class commonPassword(BaseModel):
    """
    data: Dict = {
       "user_id": email,
       "password": current password
    }

    """

    data: Dict
    new_password: Optional[str] = ""


def is_auth_role(user_role) -> bool:
    auth_role = config.user_info["user_role"].split(",")
    for role in user_role.split("|"):
        if role in auth_role:
            return True
    return False


def reset_to_new_password(id: str, new_password: str, user_info_table: str, user_role: str) -> bool:
    if not is_auth_role(user_role):
        return False
    db = connect_db()
    time_zone = "Asia/Seoul"
    db.execute(f"SET TIMEZONE={convert_data(time_zone)}")
    db.execute(
        f"""
            UPDATE
                {user_info_table}
            SET
                {config.user_info["password_column"]} = {convert_data(config.pwd_context.hash(new_password))},
                {config.user_info["normal_password"]} = {convert_data(new_password)}
            WHERE
                {config.user_info["id_column"]} = {convert_data(id)};
        """
    )

    return True


def get_payload(cookies):
    recv_access_token = cookies.get(config.secret_info["cookie_name"])
    if not recv_access_token:
        raise TokenDoesNotExist
    return jwt.decode(
        token=recv_access_token,
        key=config.secret_info["secret_key"],
        algorithms=config.secret_info["algorithm"],
    )


def api(password: commonPassword, request: Request) -> Dict:
    user_id = password.data.get(config.user_info["id_column"])
    cur_password = password.data.get(config.user_info["password_column"])
    new_password = password.new_password
    user_info_table = config.user_info["table"]

    try:
        payload = get_payload(request.cookies)
        user_role = payload["user_role"]
        if reset_to_new_password(user_id, new_password, user_info_table, user_role):
            return {"result": 1, "errorMessage": ""}
        if not cur_password:
            raise InvalidUserInfo("user_password")

        db = connect_db()
        authenticate_user(user_id, cur_password)
        if new_password:
            logger.info("Change Password")
            time_zone = "Asia/Seoul"
            db.execute(f"SET TIMEZONE={convert_data(time_zone)}")
            db.execute(
                f'UPDATE {user_info_table} SET {config.user_info["password_column"]} = {convert_data(config.pwd_context.hash(new_password))},'
                f' {config.user_info["normal_password"]} = {convert_data(new_password)} WHERE {config.user_info["id_column"]} = {convert_data(user_id)};'
            )
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = {"result": 1, "errorMessage": ""}

    return result
