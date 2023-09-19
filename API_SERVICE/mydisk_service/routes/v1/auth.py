from ast import literal_eval
import json
import logging
from datetime import datetime
from typing import Optional, Union

import bcrypt
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from starlette.responses import JSONResponse

from libs.database.connector import Executor
from mydisk_service.common.config import settings
from mydisk_service.common.const import COOKIE_NAME, LoginTable
from mydisk_service.database.conn import db


logger = logging.getLogger()

class LoginInfoWrap(BaseModel):
    """
    기존 파리미터 인터페이스와 맞추기 위해 wrap 후 유효 데이터를 삽입
    dict를 그대로 사용할 수도 있으나, 개발 편의상 자동완성을 위해 LoginInfo 객체를 생성
    """

    class LoginInfo(BaseModel):
        user_id: str
        user_password: str
        login_type: str

    data: LoginInfo

@router.post("/user/commonLogout")
async def logout():
    response = JSONResponse(status_code=200, content={"result": 1, "errorMessage": ""})
    response.delete_cookie(COOKIE_NAME, domain="bigdata-car.kr")
    return response
