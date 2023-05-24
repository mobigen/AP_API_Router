from datetime import datetime, timedelta

import bcrypt
import jwt
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from starlette.responses import JSONResponse

from libs.database.connector import Executor
from login_service.common.config import logger
from login_service.common.const import ALGORITHM, EXPIRE_DELTA, SECRET_KEY
from login_service.database.conn import db


class LoginInfo(BaseModel):
    user_id: str
    password: str = "1234"

    class Config:
        fields = {"password": {"exclude": True}}


class UserToken(BaseModel):
    user_id: str
    id: str
    name: str
    auth_cd: str
    mobile_phone: str
    phone: str
    email: str
    reg_date: str
    amd_date: str


router = APIRouter()


@router.post("/register")
async def register():
    hash_pw = bcrypt.hashpw("password".encode("utf-8"), bcrypt.gensalt())


@router.post("/login")
async def login(params: LoginInfo, request: Request, session: Executor = Depends(db.get_db)) -> JSONResponse:
    try:
        row = session.query(
            **{
                "table_nm": "user_bas",
                "where_info": [
                    {"table_nm": "user_bas", "key": "user_id", "value": params.user_id, "compare_op": "=", "op": ""}
                ],
            }
        ).first()

        if not row:
            return JSONResponse(content={"result": 0, "errorMessage": "user not found"})

        is_verified = bcrypt.checkpw(params.password.encode("utf-8"), row["password"].encode("utf-8"))
        if not is_verified:
            return JSONResponse(status_code=400, content={"result": 0, "errorMessage": "password not valid"})

        access_token = create_access_token(data=row)
        return JSONResponse(
            status_code=200,
            content={"result": 1, "errorMessage": "", "data": {"body": [{"Authorization": f"Bearer {access_token}"}]}},
        )
    except Exception as e:
        logger.error(e, exc_info=True)
        return JSONResponse(content={"result": 0, "errorMessage": ""})


def create_access_token(data: dict = None, expires_delta: int = EXPIRE_DELTA):
    to_encode = data.copy()
    if expires_delta:
        to_encode.update({"exp": datetime.utcnow() + timedelta(hours=expires_delta)})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
