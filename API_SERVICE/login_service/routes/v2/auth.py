from ast import literal_eval
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
from login_service.common.const import COOKIE_NAME, LoginTable, RegisterTable, EmailAuthTable
from login_service.database.conn import db

''''
 Status Code :
    200 : OK
    201 : Created  => create
    202 : Accepted
    204 : No Content  => modify
'''


logger = logging.getLogger()


class CreateKeycloakFailError(Exception):
    ...

class EmailAuthFail(Exception):
    ...

class AdminAuthFail(Exception):
    ...

class QueryInfoWrap(BaseModel):
    """
    기존 파리미터 인터페이스와 맞추기 위해 wrap 후 유효 데이터를 삽입
    dict를 그대로 사용할 수도 있으나, 개발 편의상 자동완성을 위해 LoginInfo 객체를 생성
    """

    class QueryInfo(BaseModel):
        query: str

    data: QueryInfo

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
        user_password: Optional[str]
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
        enabled: Optional[str]
        sub: Optional[str]

    data: RegisterInfo

class RegisterSocialInfoWrap(BaseModel):
    """
    기존 파리미터 인터페이스와 맞추기 위해 wrap 후 유효 데이터를 삽입
    dict를 그대로 사용할 수도 있으나, 개발 편의상 자동완성을 위해 LoginInfo 객체를 생성
    """

    class RegisterSocialInfo(BaseModel):
        social_type: str
        social_id: Optional[str]
        social_email: Optional[str]
        access_token: Optional[str]

    data: RegisterSocialInfo

class ActivateInfoWrap(BaseModel):
    """
    기존 파리미터 인터페이스와 맞추기 위해 wrap 후 유효 데이터를 삽입
    dict를 그대로 사용할 수도 있으나, 개발 편의상 자동완성을 위해 LoginInfo 객체를 생성
    """

    class ActivateInfo(BaseModel):
        user_id: str
        athn_no: str

    data: ActivateInfo

class UserInfoWrap(BaseModel):
    """
    기존 파리미터 인터페이스와 맞추기 위해 wrap 후 유효 데이터를 삽입
    dict를 그대로 사용할 수도 있으나, 개발 편의상 자동완성을 위해 LoginInfo 객체를 생성
    """

    class UserInfo(BaseModel):
        user_id: str

    data: UserInfo

class PasswordInfoWrap(BaseModel):
    """
    기존 파리미터 인터페이스와 맞추기 위해 wrap 후 유효 데이터를 삽입
    dict를 그대로 사용할 수도 있으나, 개발 편의상 자동완성을 위해 LoginInfo 객체를 생성
    """

    class PasswordInfo(BaseModel):
        user_id: str
        athn_no: str
        new_password: str

    data: PasswordInfo

router = APIRouter()

@router.post("/user/v2/commonLogout")
async def logout():
    response = JSONResponse(status_code=200, content={"result": 1, "errorMessage": ""})
    response.delete_cookie(COOKIE_NAME, domain="bigdata-car.kr")
    # studio cookie 삭제
    response.delete_cookie("x-access-token", domain="bigdata-car.kr")
    return response

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
    userInfo = await get_user_info_from_request(request)

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
    userInfo = await get_user_info_from_request(request)
    userData = userInfo.get("data")
    userId = userData.get("user_id")

    if userId is None:
        msg = userInfo.get("data").get("error_description")
        logger.info(msg)
        return JSONResponse(status_code=400, content={"result": 0, "errorMessage": msg})

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

    return user_upsert(session, **userParam)

@router.post("/user/v2/commonLogin")
async def login(params: LoginInfoWrap, session: Executor = Depends(db.get_db)) -> JSONResponse:
    param = params.data

    token = await get_normal_token(grant_type="password", username=param.user_id, password=param.user_password)
    logger.info(f"token :: {token}")

    if token["status_code"] == 200:
        response = JSONResponse(status_code=200, content={"result": 1, "errorMessage": ""})
        token["create_time"] = datetime.now().strftime("%s")
        response.set_cookie(key=COOKIE_NAME, value=token, domain=".bigdata-car.kr")
        return response
    else :
        return JSONResponse(
            status_code=400,
            content={"result": 0, "errorMessage": token.get("data").get("error_description")},
        )

@router.post("/user/v2/commonLoginSocial")
async def loginSocial(params: RegisterSocialInfoWrap, session: Executor = Depends(db.get_db)):
    param = params.data

    token = await get_social_token(**param.dict())
    if token["status_code"] == 200:
        token["create_time"] = datetime.now().strftime("%s")
        response = JSONResponse(status_code=200, content={"result": 1, "errorMessage": ""})
        response.set_cookie(key=COOKIE_NAME, value=token, domain=".bigdata-car.kr")
        return response
    else :
        return JSONResponse(
            status_code=400,
            content={"result": 0, "errorMessage": token.get("data").get("error_description")},
        )

@router.post("/user/v2/commonSocialLink")
async def socialLink(params: RegisterSocialInfoWrap, session: Executor = Depends(db.get_db)):
    param = params.data
    social_email = param.social_email

    admin_token = await get_admin_token()
    res = await keycloak.get_query(token=admin_token, realm=settings.KEYCLOAK_INFO.realm, query = f"username={social_email}&exact=true")

    userList = res.get("data")
    if len(userList) == 0 :
        return JSONResponse(status_code=400, content={"result": 0, "errorMessage": "Invalid User!!"})

    logger.info(f"res :: {res}")
    user_info = userList[0]
    sub = user_info.get("id")

    token = await keycloak.social_link(token=admin_token, realm=settings.KEYCLOAK_INFO.realm, sub=sub, **param.dict() )
    logger.info(f"token :: {token}")

    if token["status_code"] == 204:
        response = JSONResponse(status_code=200, content={"result": 1, "errorMessage": ""})
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
                content={"result": 1, "errorMessage": "", "data": {"body": row} }
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

@router.post("/user/v2/commonRegisterNormal")
async def registerNormal(params: RegisterInfoWrap, session: Executor = Depends(db.get_db)):
    param = params.data
    try:
        await create_keycloak_user(**param.dict())
        return JSONResponse(status_code=200, content={"result": 1, "errorMessage": ""})
    except Exception as e:
        session.rollback()
        logger.error(e, exc_info=True)
        return JSONResponse(status_code=500, content={"result": 0, "errorMessage": str(e)})

@router.post("/user/v2/commonActivateUser")
async def activateUser(params: ActivateInfoWrap, session: Executor = Depends(db.get_db)):
    param = params.data
    user_id = param.user_id
    athn_no = param.athn_no
    logger.info(param)
    try :
        await check_email_auth(user_id, athn_no, session)
        # enabled 만 True 로 변경
        reg_data = {"enabled": "true"}
        return await alter_user_info(user_id, **reg_data)
    except Exception as e:
        session.rollback()
        logger.error(e, exc_info=True)
        return JSONResponse(status_code=500, content={"result": 0, "errorMessage": str(e)})

@router.post("/user/v2/commonKeyCloakQuery")
async def getCount(params: QueryInfoWrap, session: Executor = Depends(db.get_db)):
    param = params.data
    query = param.query
    try:
        res = await get_query_keycloak(query)
        logger.info(res)
        objectCount = len(res.get("data"))
        return JSONResponse(status_code=200, content={"result": 1, "errorMessage": "","data": objectCount})
    except Exception as e:
        session.rollback()
        logger.error(e, exc_info=True)
        return JSONResponse(status_code=500, content={"result": 0, "errorMessage": str(e)})

@router.post("/user/v2/commonUserModify")
async def modify(request: Request, params: RegisterInfoWrap, session: Executor = Depends(db.get_db)):
    userInfo = await get_user_info_from_request(request)
    userInfo = userInfo.get("data")
    userId = userInfo.get("preferred_username")
    if userId is None:
        return JSONResponse(status_code=400, content={"result": 0, "errorMessage": "Invalid User"})

    param = params.data
    param.sub = userInfo.get("sub")
    return await modify_keycloak_user(**param.dict())

@router.post("/user/v2/commonAdminGetUserInfo")
async def adminGetUser(request: Request, params: UserInfoWrap):
    param = params.data
    userName = param.user_id
    try :
        await check_admin(request)

        admin_token = await get_admin_token()
        res = await keycloak.get_query(token=admin_token, realm=settings.KEYCLOAK_INFO.realm, query = f"username={userName}&exact=true")

        userList = res.get("data")
        if len(userList) != 0 :
            return JSONResponse(status_code=200, content={"result": 1, "errorMessage": "", "data": userList})
        else :
            return JSONResponse(status_code=400, content={"result": 0, "errorMessage": "Invalid User!!"})
    except Exception as e:
        session.rollback()
        logger.error(e, exc_info=True)
        return JSONResponse(status_code=500, content={"result": 0, "errorMessage": str(e)})

@router.post("/user/v2/commonAdminModifyUser")
async def adminModifyUser(request: Request, params: RegisterInfoWrap):
    param = params.data
    try :
        await check_admin(request)
        return await modify_keycloak_user(**param.dict())
    except Exception as e:
        session.rollback()
        logger.error(e, exc_info=True)
        return JSONResponse(status_code=500, content={"result": 0, "errorMessage": str(e)})

@router.post("/user/v2/commonNewPassword")
async def userNewPassword(params: PasswordInfoWrap, session: Executor = Depends(db.get_db)):
    param = params.data
    user_id = param.user_id
    athn_no = param.athn_no
    new_password = param.new_password
    logger.info(param)
    try :
        await check_email_auth(user_id, athn_no, session)
        # credentials 만 변경
        reg_data = {"credentials": [{"value": new_password}]}
        return await alter_user_info(user_id, **reg_data)
    except Exception as e:
        session.rollback()
        logger.error(e, exc_info=True)
        return JSONResponse(status_code=500, content={"result": 0, "errorMessage": str(e)})


async def check_admin(request: Request) :
    resToken = await get_user_info_from_request(request)
    logger.info(resToken)
    if resToken["status_code"] != 200 :
        raise AdminAuthFail("Required Admin Role")

    userInfo = resToken.get("data")
    userRoleList = [val.strip() for val in userInfo.get("user_role").split("|")]

    if "ROLE_ADMIN" not in userRoleList:
        raise AdminAuthFail("Required Admin Role")

async def user_upsert(session: Executor, **kwargs) :
    method = "INSERT"
    row = session.query(**LoginTable.get_query_data(kwargs.get("user_id"))).first()
    if row : method = "UPDATE"
    try :
        logger.info(kwargs)
        session.execute(auto_commit=False, **RegisterTable.upsert_query_data(method, **kwargs))
        session.commit()
        return JSONResponse(status_code=200, content={"result": 1, "errorMessage": ""})
    except Exception as e:
        session.rollback()
        logger.error(e, exc_info=True)
        return JSONResponse(status_code=500, content={"result": 0, "errorMessage": str(e)})


async def alter_user_info(user_id:str, **kwargs) :
    try:
        admin_token = await get_admin_token()
        res = await keycloak.get_query(token=admin_token, realm=settings.KEYCLOAK_INFO.realm, query = "")
        userList = res.get("data")
        user_info = list(filter(lambda item : item['username'] == user_id, userList))
        if len(user_info) == 0 :
            return JSONResponse(status_code=400, content={"result": 0, "errorMessage": "Invalid User!!"})
        user_info = user_info[0]
        sub = user_info.get("id")

        resToken = await keycloak.alter_user(token=admin_token, realm=settings.KEYCLOAK_INFO.realm, sub=sub, **kwargs)
        logger.info(f"resToken = {resToken}")
        if resToken["status_code"] == 204:
            return JSONResponse(status_code=200, content={"result": 1, "errorMessage": ""})
        else :
            return JSONResponse(
                status_code=400,
                content={"result": 0, "errorMessage": resToken.get("data").get("error_description")}
            )
    except Exception as e:
        session.rollback()
        logger.error(e, exc_info=True)
        return JSONResponse(status_code=500, content={"result": 0, "errorMessage": str(e)})

async def check_email_auth(user_id: str, athn_no: str, session: Executor) :
    email_info = session.query(**EmailAuthTable.get_query_data(user_id)).first()
    if email_info["athn_no"] == athn_no:
        email_info["athn_yn"] = "Y"
        email_info["athn_date"] = "NOW()"
        session.execute(auto_commit=False, **EmailAuthTable.get_execute_query(email_info))
    else:
        raise EmailAuthFail("EmailAuthFail")

async def get_user_info_from_request(request: Request) :
    token = request.cookies.get(COOKIE_NAME)

    if not token:
        msg = "TokenDoesNotExist"
        logger.info(msg)
        return JSONResponse(status_code=400, content={"result": 0, "errorMessage": msg})

    token = literal_eval(token)
    userInfo = await keycloak.user_info(token=token["data"]["access_token"], realm=settings.KEYCLOAK_INFO.realm )
    return userInfo

async def get_query_keycloak(query):
    admin_token = await get_admin_token()
    res = await keycloak.get_query(token=admin_token, realm=settings.KEYCLOAK_INFO.realm, query = query)
    logger.info(f"res :: {res}")
    if res["status_code"] != 200:
        raise CreateKeycloakFailError(f"CreateKeycloakFailError :: {res}")

    return res

async def modify_keycloak_user(**kwargs):
    admin_token = await get_admin_token()

    reg_data = {
        # key 이름이 "attributes"가 아닌 것은 value가 존재할때만 넣어주어야 함
        # value가 존재할때만 넣어주어야 함
        "firstName": kwargs.get("user_nm"),   # value가 존재할때만 넣어주어야 함
        "email": kwargs.get("email"),         # value가 존재할때만 넣어주어야 함
        "credentials": [{"value": kwargs.get("user_password")}],

        "emailVerified": True,            # 항상 true
        "enabled": kwargs.get("enabled"),

        # value가 존재하지 않아도 모두 넣어주어야 함
        "attributes": {
            "user_uuid":        kwargs.get("user_uuid"),
            "user_id":          kwargs.get("user_id"),
            "user_nm":          kwargs.get("user_nm"),
            "moblphon":         kwargs.get("moblphon"),
            "user_type":        kwargs.get("user_type"),
            "login_type":       kwargs.get("login_type"),
            "user_role":        kwargs.get("user_role"),
            "adm_yn":           kwargs.get("adm_yn"),
            "user_sttus":       kwargs.get("user_sttus"),
            "blng_org_cd":      kwargs.get("blng_org_cd"),
            "blng_org_nm":      kwargs.get("blng_org_nm"),
            "blng_org_desc":    kwargs.get("blng_org_desc"),
            "service_terms_yn": kwargs.get("service_terms_yn"),
            "reg_user":         kwargs.get("reg_user"),
            "reg_date":         kwargs.get("reg_date").strftime('%Y-%m-%d %H:%M:%S'),
            "amd_user":         kwargs.get("amd_user"),
            "amd_date":         kwargs.get("amd_date").strftime('%Y-%m-%d %H:%M:%S')
        }
    }

    # value가 존재할때만 넣어주어야 하는 값에 대한 처리
    if kwargs.get("user_nm") is None: del reg_data["firstName"]
    if kwargs.get("email") is None : del reg_data["email"]
    if kwargs.get("user_password") is None : del reg_data["credentials"]
    # attributes 는 하나라도 값이 None 이면 값을 넘기면 안됨
    if any(value is None for value in reg_data["attributes"].values()) : del reg_data["attributes"]

    try :
        resToken = await keycloak.alter_user(token=admin_token, realm=settings.KEYCLOAK_INFO.realm, sub=kwargs.get("sub"), **reg_data)
        logger.info(f"resToken :: {resToken}")
        if resToken["status_code"] == 204:
            return JSONResponse(status_code=200, content={"result": 1, "errorMessage": ""})
        else :
            return JSONResponse(
                status_code=400,
                content={"result": 0, "errorMessage": "Invalid User"},
            )
    except Exception as e:
        session.rollback()
        logger.error(e, exc_info=True)
        return JSONResponse(status_code=500, content={"result": 0, "errorMessage": str(e)})

async def create_keycloak_user(**kwargs):
    admin_token = await get_admin_token()
    reg_data = {
        "username": kwargs.get("user_id"),
        "firstName": kwargs.get("user_nm"),   # value가 존재할때만 넣어주어야 함
        "email": kwargs.get("email"),         # value가 존재할때만 넣어주어야 함

        "credentials": [{"value": kwargs.get("user_password")}],
        "emailVerified": True,            # 항상 true
        "enabled": True,                  # 항상 true

        "attributes": {
            "user_uuid":        kwargs.get("user_uuid"),
            "user_id":          kwargs.get("user_id"),
            "user_nm":          kwargs.get("user_nm"),
            "moblphon":         kwargs.get("moblphon"),
            "user_type":        kwargs.get("user_type"),
            "login_type":       kwargs.get("login_type"),
            "user_role":        kwargs.get("user_role"),
            "adm_yn":           kwargs.get("adm_yn"),
            "user_sttus":       kwargs.get("user_sttus"),
            "blng_org_cd":      kwargs.get("blng_org_cd"),
            "blng_org_nm":      kwargs.get("blng_org_nm"),
            "blng_org_desc":    kwargs.get("blng_org_desc"),
            "service_terms_yn": kwargs.get("service_terms_yn"),
            "reg_user":         kwargs.get("reg_user"),
            "reg_date":         kwargs.get("reg_date").strftime('%Y-%m-%d %H:%M:%S'),
            "amd_user":         kwargs.get("amd_user"),
            "amd_date":         kwargs.get("amd_date").strftime('%Y-%m-%d %H:%M:%S')
        }
    }
    res = await keycloak.create_user(token=admin_token, realm=settings.KEYCLOAK_INFO.realm, **reg_data)
    logger.info(f"res :: {res}")
    if res["status_code"] != 201:
        raise CreateKeycloakFailError(f"CreateKeycloakFailError :: {res}")

async def get_admin_token() -> None:
    res = await keycloak.generate_admin_token(
        username=settings.KEYCLOAK_INFO.admin_username,
        password=settings.KEYCLOAK_INFO.admin_password,
        grant_type="password",
    )

    return res.get("data").get("access_token")

async def get_normal_token(**kwargs):
    return await keycloak.generate_normal_token(
        realm=settings.KEYCLOAK_INFO.realm,
        client_id=settings.KEYCLOAK_INFO.client_id,
        client_secret=settings.KEYCLOAK_INFO.client_secret,
        grant_type=kwargs.pop("grant_type", "password"),
        **kwargs,
    )

async def get_social_token(**kwargs):
    return await keycloak.generate_normal_token(
        realm=settings.KEYCLOAK_INFO.realm,
        client_id=settings.KEYCLOAK_INFO.client_id,
        client_secret=settings.KEYCLOAK_INFO.client_secret,
        requested_token_type="urn:ietf:params:oauth:token-type:refresh_token",
        subject_issuer=kwargs.get("social_type"),
        subject_token=kwargs.get("access_token"),
        grant_type="urn:ietf:params:oauth:grant-type:token-exchange"
    )