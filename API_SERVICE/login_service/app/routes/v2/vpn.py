import logging
import requests

from fastapi import APIRouter, Depends, Request
from starlette.responses import JSONResponse

from libs.database.connector import Executor
from login_service.app.database.conn import db

from login_service.app.common.const import json_headers
from login_service.app.common.config import settings

logger = logging.getLogger()
router = APIRouter()


@router.post("/user/v2/VpnCheck")
async def check_vpn(request: Request, session: Executor = Depends(db.get_db)) -> JSONResponse:
    token = admin_login()

    # 2. 안랩 장비에 API로 사용자 email 주소로 사용자 생성
    # 2-1.
    url = "/object/user/account"
    payload = {
        "name": "mobigen"
    }
    headers = {
        'Authorization': token
    }
    res = requests.get(url=url, headers=headers, data=payload, verify=False)

    if res.json()['code'] == 0 :
        return res.json()['result']
    else :
        return res.json()['message']

    # 3. 생성된 사용자를 VPN 그룹에 추가
    # return JSONResponse({"result": 0})


def admin_login():
    payload = {
        "id": settings.VPN_INFO.VPN_ID,
        "password": settings.VPN_INFO.VPN_PASS
    }
    print(payload)
    res = requests.post(url=f"{settings.VPN_INFO.VPN_URL}/token", headers=json_headers, data=payload, verify=False)
    print(res)
    if res.json()["code"] == 0:
        pass
    token = res.json()['token']
    # 1-2. token check
    headers = {
        'Authorization': token
    }
    res = requests.post(url=f"{settings.VPN_INFO.VPN_URL}/login", headers=headers, verify=False)
    print("login", res.json())
    print(res.json()['message'])
    return token
