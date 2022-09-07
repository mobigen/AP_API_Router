from typing import Dict, Optional
from pydantic import BaseModel
from fastapi.logger import logger
from datetime import datetime, timedelta
from jose import jwt
from Utils.CommonUtil import connect_db, get_exception_info
from Utils.DataBaseUtil import convert_data
from ApiService.ApiServiceConfig import config


class IncorrectUserName(Exception):
    pass


class IncorrectPassword(Exception):
    pass


class commonLogin(BaseModel):
    data: Dict


def verify_password(plain_password, hashed_password):
    return config.pwd_context.verify(plain_password, hashed_password)


def get_user(user_name: str):
    db = connect_db()
    user = db.select(
        f'SELECT * FROM {config.user_info["table"]} WHERE {config.user_info["id_column"]} = {convert_data(user_name)}')
    print(f"USER: {user[0]}")
    return user


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user[0]:
        raise IncorrectUserName
    user = user[0][0]
    if not verify_password(password, user[config.user_info["password_column"]]):
        raise IncorrectPassword
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


def api(login: commonLogin) -> Dict:
    try:
        user = authenticate_user(
            login.data[config.user_info["id_column"]], login.data[config.user_info["password_column"]])
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        access_token = create_token(
            data={"sub": user[config.user_info["id_column"]]}, expires_delta=timedelta(minutes=int(config.secret_info["expire_min"])))
        result = {"result": 1, "errorMessage": "", "data": {
            "access_token": access_token, "token_type": "bearer"}}

    return result
