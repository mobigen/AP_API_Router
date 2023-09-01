from ast import literal_eval
import json
import logging
from datetime import datetime
from typing import Optional, Union

import bcrypt
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from starlette.responses import JSONResponse
from libs.auth.keycloak import keycloak

from libs.database.connector import Executor
from login_service.common.config import settings
from login_service.common.const import COOKIE_NAME, LoginTable, RegisterTable
from login_service.database.conn import db


logger = logging.getLogger()


class CreateKeycloakFailError(Exception):
    ...


class LoginInfoWrap(BaseModel):
    """
    기존 파리미터 인터페이스와 맞추기 위해 wrap 후 유효 데이터를 삽입
    dict를 그대로 사용할 수도 있으나, 개발 편의상 자동완성을 위해 LoginInfo 객체를 생성
    """

    class LoginInfo(BaseModel):
        user_id: str
        user_password: str

    data: LoginInfo


class RegisterInfoWrap(BaseModel):
    """
    기존 파리미터 인터페이스와 맞추기 위해 wrap 후 유효 데이터를 삽입
    dict를 그대로 사용할 수도 있으나, 개발 편의상 자동완성을 위해 RegisterInfo 객체를 생성
    """

    class RegisterInfo(BaseModel):
        user_id: str
        user_password: str
        login_type: Optional[str] = "MEMBER"
        user_type: Optional[str] = "GENL"
        user_sttus: Optional[str] = "SBSCRB"
        user_nm: Optional[str]
        email: Optional[str]
        moblphon: Optional[str]
        blng_org_cd: Optional[str] = None
        blng_org_nm: Optional[str] = None
        blng_org_desc: Optional[str] = None
        service_terms_yn: Optional[str] = "Y"
        pwd_fail_tms: Optional[int]
        login_fail_date: Optional[datetime]
        last_login_date: Optional[datetime]
        reg_date: Union[datetime, str] = "NOW()"
        amd_date: Union[datetime, str] = datetime.now()
        user_uuid: Optional[str]
        reg_user: Optional[str]
        amd_user: Optional[str]
        user_role: Optional[str]
        user_normal: Optional[str]
        adm_yn: Optional[str]

    data: RegisterInfo


router = APIRouter()
@router.get("/user/v2/commonUserInfo")
async def info(request: Request, session: Executor = Depends(db.get_db)):
    """
    {
        "result": 1,
        "errorMessage": "",
        "data": {
            "body": {
                "user_id": "admin@test.com",
                "email": "admin@test.com",
                "login_type": "MEMBER",
                "moblphon": "010-1111-1112",
                "user_nm": "관리자",
                "user_type": "GENL",
                "user_role": "ROLE_USER|ROLE_ADMIN",
                "user_uuid": "6d77d874-e613-480f-8e86-dba491c28167",
                "blng_org_cd": "None",
                "blng_org_nm": "None",
                "blng_org_desc": "None",
                "exp": 1689053022
            }
        }
    }

    Args:
        request (Request): _description_
        session (Executor, optional): _description_. Defaults to Depends(db.get_db).
    """
    token = request.cookies.get(COOKIE_NAME)

    if not token:
        msg = "TokenDoesNotExist"
        logger.info(msg)
        return JSONResponse(status_code=400, content={"result": 0, "errorMessage": msg})

    token = literal_eval(token)
    userInfo = await keycloak.user_info(token=token["data"]["access_token"], realm=settings.KEYCLOAK_INFO.realm )

    if userInfo.get("status_code") == 200 :
        return JSONResponse(
            status_code=200,
            content={"result": 1, "errorMessage": "", "data": {"body": userInfo.get("data")}},
        )
    else :
        return JSONResponse(
            status_code=400,
            content={"result": 0, "errorMessage": userInfo.get("data").get("error_description")},
        )
@router.get("/user/v2/commonUserUpsert")
async def register(request: Request, session: Executor = Depends(db.get_db)):
    """
    {
        "result": 1,
        "errorMessage": "",
        "data": {
            "body": {
                "user_id": "admin@test.com",
                "email": "admin@test.com",
                "login_type": "MEMBER",
                "moblphon": "010-1111-1112",
                "user_nm": "관리자",
                "user_type": "GENL",
                "user_role": "ROLE_USER|ROLE_ADMIN",
                "user_uuid": "6d77d874-e613-480f-8e86-dba491c28167",
                "blng_org_cd": "None",
                "blng_org_nm": "None",
                "blng_org_desc": "None",
                "exp": 1689053022
            }
        }
    }

    Args:
        request (Request): _description_
        session (Executor, optional): _description_. Defaults to Depends(db.get_db).
    """
    token = request.cookies.get(COOKIE_NAME)

    if not token:
        msg = "TokenDoesNotExist"
        logger.info(msg)
        return JSONResponse(status_code=400, content={"result": 0, "errorMessage": msg})

    token = literal_eval(token)
    userInfo = await keycloak.user_info(token=token["data"]["access_token"], realm=settings.KEYCLOAK_INFO.realm )
    userData = userInfo.get("data")
    userId = userData.get("user_id")

    if userId == None:
        msg = userInfo.get("data").get("error_description")
        logger.info(msg)
        return JSONResponse(status_code=400, content={"result": 0, "errorMessage": msg})
    return

    userParam = {
       "keycloak_uuid": userData.get("sub"),
       "user_uuid": userData.get("user_uuid"),
       "user_id": userData.get("user_id"),
       "user_nm": userData.get("user_nm"),
       "email": userData.get("email"),
       "moblphon": userData.get("moblphon"),
       "user_type": userData.get("user_type"),
       "login_type": userData.get("login_type"),
       "user_role": userData.get("user_role"),
       "adm_yn": userData.get("adm_yn"),
       "user_sttus": userData.get("user_sttus"),
       "blng_org_cd": userData.get("blng_org_cd"),
       "blng_org_nm": userData.get("blng_org_nm"),
       "blng_org_desc": userData.get("blng_org_desc"),
       "service_terms_yn": userData.get("service_terms_yn"),
       "reg_user": userData.get("reg_user"),
       "reg_date": userData.get("reg_date"),
       "amd_user": userData.get("amd_user"),
       "amd_date": userData.get("amd_date")
    }

    method = "INSERT"
    row = session.query(**LoginTable.get_query_data(userId)).first()
    if row : method = "UPDATE"
    try :
        logger.info(userParam)
        session.execute(auto_commit=False, **RegisterTable.upsert_query_data(method, userParam))
        session.commit()
        return JSONResponse(status_code=200, content={"result": 1, "errorMessage": ""})
    except Exception as e:
        session.rollback()
        logger.error(e, exc_info=True)
        return JSONResponse(status_code=500, content={"result": 0, "errorMessage": str(e)})

@router.post("/user/v2/commonLogin")
async def login(params: LoginInfoWrap, session: Executor = Depends(db.get_db)) -> JSONResponse:
    param = params.data

    token = await get_normal_token(grant_type="password", username=param.user_id, password=param.user_password)
    logger.info(f"token :: {token}")

    if token["status_code"] == 200:
        response = JSONResponse(status_code=200, content={"result": 1, "errorMessage": ""})
        response.set_cookie(key=COOKIE_NAME, value=token)
        return response
    else :
        return JSONResponse(
            status_code=400,
            content={"result": 0, "errorMessage": token.get("data").get("error_description")},
        )

@router.post("/user/v2/commonLoginDB")
async def loginDB(params: LoginInfoWrap, session: Executor = Depends(db.get_db)) -> JSONResponse:
    param = params.data

    check_pw = True
    try :
        row = session.query(**LoginTable.get_query_data(param.user_id)).first()
        check_pw = bcrypt.checkpw(param.user_password.encode('utf-8'), row["user_password"].encode('utf-8'))

        if row and check_pw:
            return JSONResponse(
                status_code=200,
                content={"result": 0, "errorMessage": "", "data": {"body": row} }
            )
        else :
            return JSONResponse(
                status_code=200,
                content={"result": 0, "errorMessage": "no user" }
            )
    except Exception as e:
        logger.error(e, exc_info=True)
        logger.error(f"data :: {params}")
        return JSONResponse(status_code=500, content={"result": 0, "errorMessage": str(e)})

async def get_normal_token(**kwargs):
    return await keycloak.generate_normal_token(
        realm=settings.KEYCLOAK_INFO.realm,
        client_id=settings.KEYCLOAK_INFO.client_id,
        client_secret=settings.KEYCLOAK_INFO.client_secret,
        grant_type=kwargs.pop("grant_type", "password"),
        **kwargs,
    )
