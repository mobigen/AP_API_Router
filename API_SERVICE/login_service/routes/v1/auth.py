import logging
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
import jwt
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from starlette.responses import JSONResponse

from libs.database.connector import Executor
from login_service.common.const import ALGORITHM, EXPIRE_DELTA, SECRET_KEY
from login_service.database.conn import db


logger = logging.getLogger()


class LoginInfo(BaseModel):
    user_id: str
    password: str


class RegisterInfo(BaseModel):
    usridx: str
    id: str
    pwd: str
    nm: Optional[str]
    mbphne: Optional[str]
    phne: Optional[str]
    email: Optional[str]
    deptidx: Optional[str]
    roleidx: Optional[str]
    aprvusr: Optional[str]
    aprvyn: Optional[str]
    useyn: Optional[str]
    rgstusridx: Optional[str]
    mdfcusridx: Optional[str]
    rgstdt: Optional[str]
    mdfcdt: Optional[str]


class UserToken(BaseModel):
    usridx: str
    id: str
    pwd: str
    nm: Optional[str]
    mbphne: Optional[str]
    phne: Optional[str]
    email: Optional[str]
    deptidx: Optional[str]
    roleidx: Optional[str]
    aprvusr: Optional[str]
    aprvyn: Optional[str]
    useyn: Optional[str]
    rgstusridx: Optional[str]
    mdfcusridx: Optional[str]
    rgstdt: Optional[str]
    mdfcdt: Optional[str]

    class Config:
        fields = {"pwd": {"exclude": True}}


router = APIRouter()


@router.post("/user/register")
async def register(params: RegisterInfo, session: Executor = Depends(db.get_db)):
    hash_pw = bcrypt.hashpw(params.pwd.encode("utf-8"), bcrypt.gensalt()).decode(encoding="utf-8")
    params.pwd = hash_pw
    try:
        session.execute(method="INSERT", table_nm="usr_mgmt", data=params.dict())
        return JSONResponse(status_code=200, content={"result": 1, "errorMessage": ""})
    except Exception as e:
        return JSONResponse(status_code=500, content={"result": 0, "errorMessage": str(e)})


@router.post("/user/login")
async def login(params: LoginInfo, session: Executor = Depends(db.get_db)) -> JSONResponse:
    try:
        row = session.query(
            table_nm="USR_MGMT",
            where_info=[{"table_nm": "USR_MGMT", "key": "id", "value": params.user_id, "compare_op": "=", "op": ""}],
        ).first()

        if not row:
            return JSONResponse(content={"result": 0, "errorMessage": "user not found"})

        is_verified = bcrypt.checkpw(params.password.encode("utf-8"), row["pwd"].encode("utf-8"))
        if not is_verified:
            return JSONResponse(status_code=400, content={"result": 0, "errorMessage": "password not valid"})

        access_token = create_access_token(data=UserToken(**row).dict())
        return JSONResponse(
            status_code=200,
            content={"result": 1, "errorMessage": "", "data": {"body": [{"Authorization": f"{access_token}"}]}},
        )
    except Exception as e:
        logger.error(e, exc_info=True)
        return JSONResponse(content={"result": 0, "errorMessage": ""})


@router.get("/user/info")
async def info(request: Request):
    token = request.headers.get("Authorization")
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
    except jwt.DecodeError as e:
        logger.error(f"{e}, token :: {token}", exc_info=True)


def create_access_token(data: dict = None, expires_delta: int = EXPIRE_DELTA):
    to_encode = data.copy()
    if expires_delta:
        to_encode.update({"exp": datetime.utcnow() + timedelta(hours=expires_delta)})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
