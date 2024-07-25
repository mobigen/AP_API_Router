import json
import logging
import requests

from pydantic import BaseModel
from fastapi import APIRouter
from starlette.responses import JSONResponse

from login_service.app.common.const import json_headers
from login_service.app.common.config import settings

logger = logging.getLogger()
router = APIRouter()


class InfoWrap(BaseModel):
    class Info(BaseModel):
        email: str

    data: Info


@router.post("/user/v2/CheckVpn")
async def check_vpn(params: InfoWrap) -> JSONResponse:
    param = params.data
    email = param.email

    header = get_admin_header()
    payload = {"name": email}
    try:
        res = requests.get(
            url=f"{settings.VPN_INFO.VPN_URL}/object/user/account",
            headers=header,
            data=json.dumps(payload),
            verify=False
        )
        logger.info(res.json())
        admin_logout(header)
        return result_format(res)
    except Exception as e:
        admin_logout(header)
        return result_error(e)


@router.post("/user/v2/JoinVpn")
def create_vpn(params: InfoWrap) -> JSONResponse:
    param = params.data
    email = param.email

    header = get_admin_header()
    payload = {
        "name": email,
        "password": settings.VPN_INFO.VPN_PASS,
        "auth_type": "0",                   # 인증 유형 password
        "security_level": "0",              # 보안 등급 높음
        "expire_date": settings.VPN_INFO.VPN_EXPIRE,
        "certificate_issue_enable": "0",    # 인증서 없음
        "personal_id_enable": "0",          # 개인식별번호 사용 안함
    }
    try:
        res = requests.post(
            url=f"{settings.VPN_INFO.VPN_URL}/object/user/account",
            headers=header,
            data=json.dumps(payload),
            verify=False
        )
        logger.info(res.json())
        try:
            edit_group(header, settings.VPN_INFO.VPN_GROUP, email, "add")
        except Exception:
            pass
        apply(header)
        admin_logout(header)
        return result_format(res)
    except Exception as e:
        admin_logout(header)
        return result_error(e)


@router.post("/user/v2/DropVpn")
def delete_vpn(params: InfoWrap) -> JSONResponse:
    param = params.data
    email = param.email

    header = get_admin_header()
    payload = {"name": email}
    try:
        try:
            edit_group(header, settings.VPN_INFO.VPN_GROUP, email, "del")
        except Exception:
            pass
        res = requests.delete(
            url=f"{settings.VPN_INFO.VPN_URL}/object/user/account",
            headers=header,
            data=json.dumps(payload),
            verify=False
        )
        logger.info(res.json())
        apply(header)
        admin_logout(header)
        return result_format(res)
    except Exception as e:
        admin_logout(header)
        return result_error(e)


def get_admin_header():
    payload = {
        "id": settings.VPN_INFO.VPN_ID,
        "password": settings.VPN_INFO.VPN_PASS
    }
    res = requests.post(
        url=f"{settings.VPN_INFO.VPN_URL}/token",
        headers=json_headers,
        data=json.dumps(payload),
        verify=False
    )

    if res.json()["code"] != 0:
        logger.info(res.json()["code"])
        raise ValueError(res.json())

    token = res.json()['token']
    header = {'Authorization': token}
    res = requests.post(
        url=f"{settings.VPN_INFO.VPN_URL}/login",
        headers=header,
        verify=False
    )
    logger.info("login", res.json())
    return header


def admin_logout(header):
    try:
        res = requests.post(
            url=f"{settings.VPN_INFO.VPN_URL}/logout",
            headers=header,
            verify=False
        )
        logger.info(res.json())
    except Exception as e:
        return result_error(e)


def apply(header):
    try :
        res = requests.post(
            url=f"{settings.VPN_INFO.VPN_URL}/apply",
            headers=header,
            verify=False
        )
        logger.info(res.json())
    except Exception as e:
        return result_error(e)


def edit_group(header, group_name, email, mode):

    res = get_group_info(header, group_name)
    emailList = res[0]["member_list"].split(";")
    if mode == "add":
        if email not in emailList :
            emailList.append(email)
    else:  # del
        if email in emailList :
            emailList.pop(emailList.index(email))

    payload = json.dumps({
        "name": group_name,
        "member_list": ";".join(emailList)
    })

    res = requests.put(url=f"{settings.VPN_INFO.VPN_URL}/object/user/group", data=payload, headers=header, verify=False)
    if res.json()['code'] == 0:
        return res.json()['message']
    else:
        return res.json()['message']


def get_group_info(header, group_name):
    payload = json.dumps({
        "name": group_name
    })

    res = requests.get(url=f"{settings.VPN_INFO.VPN_URL}/object/user/group", data=payload, headers=header, verify=False)

    if res.json()['code'] == 0:
        return res.json()['result']
    else:
        return res.json()['message']


def result_format(res):
    if res.json()["code"] == 0:
        return JSONResponse(
            status_code=200,
            content={"result": 1, "errorMessage": "", "data": res.json()["message"]}
        )
    else:
        return JSONResponse(
            status_code=200,
            content={"result": 1, "errorMessage": "", "data": res.json()["message"]}
        )


def result_error(e):
    logger.error(e, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"result": 0, "errorMessage": str(e)}
    )
