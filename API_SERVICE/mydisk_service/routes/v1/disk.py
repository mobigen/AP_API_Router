import os
import json
import bcrypt
import logging

from pathlib import Path
from ast import literal_eval
from datetime import datetime
from typing import Optional, Union

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from starlette.responses import JSONResponse

from libs.auth.keycloak import keycloak
from libs.disk.mydisk import mydisk
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

class Params(BaseModel):
    target_file_directory: str
    rows: int

    def get_path(self) -> Path:
        return Path(
            os.path.join(
                settings.MYDISK_ROOT_DIR,
                self.target_file_directory.lstrip("/")
                if self.target_file_directory.startswith("/")
                else self.target_file_directory,
            )
        )


router = APIRouter()


@router.post("/preview")
async def head(params: Params):
    try:
        path = params.get_path()
        lines = params.rows
        #df = pd.read_excel(path, header=None) if path.suffix in [".xls", ".xlsx"] else pd.read_csv(path, header=None)
        #df = df.fillna("")
        #result = {"result": 1, "errorMessage": "", "data": {"body": df[:lines].values.tolist()}}
        return JSONResponse(status_code=500, content={"result": 1, "errorMessage": "", "data": {"body": "TEST"}})
    except Exception as e:
        result = {"result": 1, "errorMessage": str(e)}
    return result

async def get_admin_token() -> None:
    res = await mydisk.generate_admin_token(
        username=settings.MYDISK_INFO.admin_username,
        password=settings.MYDISK_INFO.admin_password,
        scope=settings.MYDISK_INFO.scope,
        client_id=settings.MYDISK_INFO.client_id,
        client_secret=settings.MYDISK_INFO.client_secret,
    )

    return res.get("data").get("access_token")
