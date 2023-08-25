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


@router.post("/user/commonRegister")
async def register(params: RegisterInfoWrap, session: Executor = Depends(db.get_db)):
    param = params.data
    param.user_normal = param.user_password
    param.user_password = bcrypt.hashpw(param.user_password.encode("utf-8"), bcrypt.gensalt()).decode(encoding="utf-8")
    try:
        logger.info(params)
        row = session.query(**LoginTable.get_query_data(param.user_id)).first()
        logger.info(f"row:: {row}")
        if row:
            return JSONResponse(status_code=200, content={"result": 1, "errorMessage": "Already registered"})

        session.execute(auto_commit=False, **RegisterTable.get_query_data(param.dict()))

        await create_keycloak_user(**param.dict())

        session.commit()
        return JSONResponse(status_code=200, content={"result": 1, "errorMessage": ""})
    except Exception as e:
        session.rollback()
        logger.error(e, exc_info=True)
        return JSONResponse(status_code=500, content={"result": 0, "errorMessage": str(e)})


@router.post("/user/commonLogin")
async def login(params: LoginInfoWrap, session: Executor = Depends(db.get_db)) -> JSONResponse:
    """
        keycloak 인중 후 토큰 발급
        table data
        {
            'user_id': 'swyang',
            'user_password': '$2b$12$eL47K7Pi5.Ee9GCTftZ1GuwFMO96jFltAuhnMvropsu/JtyzB26UO',
            'login_type': None,
            'user_type': None,
            'user_sttus': None,
            'user_nm': 'seok',
            'email': 'test@test.com',
            'moblphon': None,
            'blng_org_cd': None,
            'blng_org_nm': None,
            'blng_org_desc': None,
            'service_terms_yn': None,
            'pwd_fail_tms': None,
            'login_fail_date': None,
            'last_login_date': None,
            'reg_date': None,
            'amd_date': None,
            'user_uuid': None,
            'reg_user': None,
            'amd_user': None,
            'user_role': None,
            'user_normal': 'zxcv1234!',
            'adm_yn': None
        }

    Args:
        params (LoginInfoWrap): _description_
        session (Executor, optional): _description_. Defaults to Depends(db.get_db).

    Returns:
        JSONResponse: _description_
    """
    param = params.data
    try:
        row = session.query(**LoginTable.get_query_data(param.user_id)).first()
        if not row:
            return JSONResponse(status_code=400, content={"result": 0, "errorMessage": "id or password not found"})

        token = await get_normal_token(grant_type="password", username=param.user_id, password=row["user_password"])
        logger.info(f"token :: {token}")
        if token["status_code"] == 401:
            await create_keycloak_user(**row)

        response = JSONResponse(status_code=200, content={"result": 1, "errorMessage": ""})
        response.set_cookie(key=COOKIE_NAME, value=token)
        return response
    except Exception as e:
        logger.error(e, exc_info=True)
        logger.error(f"data :: {params}")
        return JSONResponse(status_code=500, content={"result": 0, "errorMessage": str(e)})


@router.get("/user/commonUserInfo")
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
    logger.info(f"type :: {type(token)}, token :: {token}")
    username = await username_from_token(token["data"]["access_token"])
    row = session.query(**LoginTable.get_query_data(username)).first()

    return JSONResponse(
        status_code=200,
        content={"result": 1, "errorMessage": "", "data": {"body": row}},
    )


@router.post("/user/commonLogout")
async def logout():
    response = JSONResponse(status_code=200, content={"result": 1, "errorMessage": ""})
    response.delete_cookie(COOKIE_NAME)
    return response


async def get_admin_token() -> None:
    res = await keycloak.generate_admin_token(
        username=settings.KEYCLOAK_INFO.admin_username,
        password=settings.KEYCLOAK_INFO.admin_password,
        grant_type="password",
    )

    return res.get("data").get("access_token")


async def create_keycloak_user(**kwargs):
    admin_token = await get_admin_token()
    logger.info(kwargs)
    logger.info(f"admin_token :: {admin_token}")
    reg_data = {
        "username": kwargs["user_id"],
        "firstName": kwargs["user_nm"],
        "email": kwargs["email"],
        "emailVerified": True,
        "enabled": True,
        "credentials": [{"value": kwargs["user_password"]}],
        "attributes": json.dumps(kwargs, default=str),
    }
    logger.info(f"reg_data :: {reg_data}")
    res = await keycloak.create_user(token=admin_token, realm=settings.KEYCLOAK_INFO.realm, **reg_data)
    logger.info(f"res :: {res}")
    if res["status_code"] != 201:
        raise CreateKeycloakFailError(f"CreateKeycloakFailError :: {res}")


async def get_normal_token(**kwargs):
    return await keycloak.generate_normal_token(
        realm=settings.KEYCLOAK_INFO.realm,
        client_id=settings.KEYCLOAK_INFO.client_id,
        client_secret=settings.KEYCLOAK_INFO.client_secret,
        grant_type=kwargs.pop("grant_type", "password"),
        **kwargs,
    )


async def username_from_token(access_token: str):
    logger.info(access_token)
    res = await keycloak.user_info(
        realm=settings.KEYCLOAK_INFO.realm,
        token=access_token,
    )
    logger.info(f"token info res :: {res}")
    return res["data"]["preferred_username"]


async def delete_user(**kwargs):
    """
    keycloak delete api 호출
    params:
        user_id: str
    """
    admin_token = await get_admin_token()
    res = await keycloak.delete_user(
        token=admin_token, realm=settings.KEYCLOAK_INFO.realm, user_id=kwargs.get("user_id")
    )
    logger.info(f"delete res :: {res}")
