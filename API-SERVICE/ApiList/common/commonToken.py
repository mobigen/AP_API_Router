from typing import Dict, Optional
from fastapi.logger import logger
from datetime import datetime, timedelta
from jose import jwt
from Utils.CommonUtil import connect_db, get_exception_info
from Utils.DataBaseUtil import convert_data
from ApiService.ApiServiceConfig import config
from starlette.requests import Request


class InvalidUserInfo(Exception):
    pass


class TokenDoesNotExist(Exception):
    pass


def get_user(user_name: str):
    db = connect_db()
    user = db.select(
        f'SELECT * FROM {config.user_info["table"]} WHERE {config.user_info["id_column"]} = {convert_data(user_name)}')
    return user


def create_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode, config.secret_info["secret_key"], algorithm=config.secret_info["algorithm"])
    return encoded_jwt


def api(request: Request) -> Dict:
    try:
        access_token = request.headers.get(config.secret_info["header_name"])
        if not access_token:
            raise TokenDoesNotExist
        payload = jwt.decode(token=access_token,
                             key=config.secret_info["secret_key"], algorithms=config.secret_info["algorithm"])

        username = payload["sub"]
        user = get_user(username)
        if not user[0]:
            raise InvalidUserInfo
        user = user[0][0]
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        access_token = create_token(data={"sub": user[config.user_info["id_column"]]}, expires_delta=timedelta(
            minutes=int(config.secret_info["expire_min"])))

        result = {"result": 1, "errorMessage": "", "data": {
            "access_token": access_token, "token_type": "bearer"}}
    return result
