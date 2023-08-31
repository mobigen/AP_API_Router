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
        login_type: str

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
    userData = userInfo.get("data")
    userId = userData.get("user_id")
    row = session.query(**LoginTable.get_query_data(userId)).first()
    logger.info(f"row:: {row}")

    '''
    {
       "status_code":200,
       "data":{
          "sub":"3b3e4411-e1d7-48e8-bdb4-aefde2225356",
          "blng_org_cd":"BLNG_ORG_3",
          "email_verified":true,
          "login_type":"MEMBER",
          "reg_user":"792a8948-6c78-4228-90a6-cf53dbdfe2ac",
          "user_nm":"김준영",
          "preferred_username":"kjy9337@gmail.com",
          "given_name":"김준영",
          "blng_org_desc":"테스트",
          "user_sttus":"SBSCRB",
          "blng_org_nm":"한국교통연구원",
          "adm_yn":"N",
          "reg_date":"2022-10-06 10:37:16.188364",
          "user_role":"ROLE_INSTN",
          "amd_date":"2022-10-06 10:37:16.188364",
          "user_uuid":"792a8948-6c78-4228-90a6-cf53dbdfe2ac",
          "user_type":"INSTN",
          "user_id":"kjy9337@gmail.com",
          "moblphon":"010-0000-0002",
          "name":"김준영",
          "amd_user":"792a8948-6c78-4228-90a6-cf53dbdfe2ac",
          "email":"kjy9337@gmail.com",
          "service_terms_yn":"Y"
       }
    }
    '''


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

    logger.info(**RegisterTable.get_query_data(userParam))

    '''
    if row :
        session.execute(auto_commit=False, **RegisterTable.get_query_data(userParam.dict()))
    else :

    if resToken.get("status_code") == 200 :
        return JSONResponse(
            status_code=200,
            content={"result": 1, "errorMessage": "", "data": {"body": resToken.get("data")}},
        )
    else :
        return JSONResponse(
            status_code=400,
            content={"result": 0, "errorMessage": resToken.get("data").get("error_description")},
        )
    '''

