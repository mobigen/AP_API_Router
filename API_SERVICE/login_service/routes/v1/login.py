from datetime import datetime, timedelta
from typing import Any, Union
import jwt
from login_service.common.const import ALGORITHM, COOKIE_NAME, EXPIRE_DELTA, SECRET_KEY
from login_service.database.conn import db
from login_service.common.config import logger
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse


class LoginInfo(BaseModel):
    user_id: str
    password: str = "1234"

    class Config:
        fields = {"password": {"exclude": True}}


router = APIRouter()


@router.post("/login")
async def login(params: LoginInfo, request: Request, session: Union[Session, Any] = Depends(db.get_db)) -> JSONResponse:
    try:
        row = db.query(
            **{
                "table_nm": "user_bas",
                "where_info": [
                    {"table_nm": "user_bas", "key": "user_id", "value": params.user_id, "compare_op": "=", "op": ""}
                ],
            }
        ).first()

        if not row:
            return JSONResponse(content={"result": 0, "errorMessage": "user not found"})

        if row["password"] != params.password:
            # TODO: 암호화 복호화 필요?
            return JSONResponse(content={"result": 0, "errorMessage": "password not valid"})

        access_token = create_access_token(data=row)

        response = JSONResponse(content={"result": 1, "errorMessage": ""})
        response.set_cookie(
            key=COOKIE_NAME,
            value=access_token,
            max_age=3600,
            secure=False,
            httponly=True,
        )

        return response
    except Exception as e:
        logger.error(e, exc_info=True)
        return JSONResponse(content={"result": 0, "errorMessage": ""})


def create_access_token(data: dict = None, expires_delta: int = EXPIRE_DELTA):
    to_encode = data.copy()
    if expires_delta:
        to_encode.update({"exp": datetime.utcnow() + timedelta(hours=expires_delta)})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
