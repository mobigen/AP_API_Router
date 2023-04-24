import copy
import json

import aiohttp
from app.common import const
from app.common.config import logger
from libs.database.conn import db
from app.database.models import TbApiInfo
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import JSONResponse

router = APIRouter()


@router.get("/route/common/me")
async def me(request: Request):
    return {"result": 1, "errorMesage": "", "data": request.scope["client"][0]}


@router.api_route("/{route_path:path}", methods=["GET", "POST"])
async def index(request: Request, route_path: str, session: Session = Depends(db.get_db)):
    method = request.method
    headers = get_headers(request.headers)
    query_params = request.query_params
    data = None
    if method == "POST":
        try:
            data = await request.json()
        except json.JSONDecodeError:
            data = (await request.body()).decode()

    tb_api_info: TbApiInfo = TbApiInfo.filter(session, route_url="/" + route_path, mthd=method).first()
    if not tb_api_info:
        logger.error(f"API INFO NOT FOUND, url :: {route_path}, method :: {method}")
        return JSONResponse(content={"result": 0, "errorMessage": "API INFO NOT FOUND."}, status_code=404)

    remote_url = "http://" + tb_api_info.server_info.ip_adr + tb_api_info.url

    cookies = {}
    try:
        cookies, result = await request_to_service(remote_url, method, query_params, data, headers)
    except Exception as e:
        logger.error(e, exc_info=True)
        result = {"result": 0, "errorMessage": type(e).__name__}

    response = JSONResponse(content=result)
    for k, v in cookies.items():
        response.set_cookie(key=k, value=v, max_age=3600, secure=False, httponly=True)

    return response


def get_headers(h) -> dict:
    """
    헤더를 제거하지 않을경우 postman에서 timeout 발생
    (aiohttp request를 요청할때)
    """
    headers = copy.deepcopy(dict(h))
    for exclude in const.EXCLUDE_HEADERS:
        if exclude in headers:
            del headers[exclude]
    return headers


async def request_to_service(url, method, params, data, headers):
    async with aiohttp.ClientSession() as session:
        async with session.request(url=url, method=method, params=params, json=data, headers=headers) as response:
            return dict(response.cookies), await response.json()
