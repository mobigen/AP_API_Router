import json
import logging
import requests

from pydantic import BaseModel
from fastapi import APIRouter, Depends, Request
from starlette.responses import JSONResponse

from libs.database.connector import Executor
from login_service.app.database.conn import db

from login_service.app.common.const import json_headers
from login_service.app.common.config import settings

logger = logging.getLogger()
router = APIRouter()


class Input(BaseModel):
    email: str


@router.post("/user/v2/CheckVpn")
async def check_vpn(input: Input) -> JSONResponse:
    token = admin_login()
    payload = json.dumps({"name": input.email})
    headers = {'Authorization': token}
    res = requests.get(url=f"{settings.VPN_INFO.VPN_URL}/object/user/account", headers=headers, data=payload, verify=False)
    print(res.json())
    if res.json()['code'] == 0:
        print(res.json()['result'])
        return JSONResponse(
            status_code=200,
            content={"result": 0, "errorMessage": ""},
        )
    else:
        print(res.json()['message'])
        return JSONResponse(
            status_code=400,
            content={"result": 0, "errorMessage": ""},
        )


@router.post("/user/v2/JoinVpn")
def create_vpn(input: Input):
    token = admin_login()
    headers = {
        'Authorization': token
    }
    payload = json.dumps({
        "name": input.email,
        "password": settings.VPN_INFO.VPN_PASS,
        "auth_type": "0", # 인증 유형 password
        "security_level": "0", # 보안 등급 높음
        "expire_date": "20281231", # 다른 기준과 동일하게 변경
        "certificate_issue_enable": "0", # 인증서 없음
        "personal_id_enable": "0", # 개인식별번호 사용 안함
    })
    res = requests.post(url=f"{settings.VPN_INFO.VPN_URL}/object/user/account", headers=headers, data=payload, verify=False)
    print(res.json())

    return res.json()['message']


@router.post("/user/v2/DropVpn")
def delete_vpn(input: Input):
    token = admin_login()
    payload = json.dumps({"name": input.email})
    headers = {
        'Authorization': token
    }
    res = requests.delete(url=f"{settings.VPN_INFO.VPN_URL}/object/user/account", headers=headers, data=payload, verify=False)

    return res.json()['message']


def admin_login():
    payload = json.dumps({
        "id": settings.VPN_INFO.VPN_ID,
        "password": settings.VPN_INFO.VPN_PASS
    })
    res = requests.post(url=f"{settings.VPN_INFO.VPN_URL}/token", headers=json_headers, data=payload, verify=False)

    if res.json()["code"] != 0:
        print(res.json()["code"])
        raise ValueError(res.json())

    token = res.json()['token']
    # 1-2. token check
    headers = {
        'Authorization': token
    }
    res = requests.post(url=f"{settings.VPN_INFO.VPN_URL}/login", headers=headers, verify=False)
    print("login", res.json())
    print(res.json()['message'])
    return token