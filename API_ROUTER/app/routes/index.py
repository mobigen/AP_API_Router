import copy
import json
import logging
from datetime import datetime

import aiohttp
from fastapi import APIRouter, Depends
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.common import const
from app.database.conn import db
from libs.database.connector import Executor

logger = logging.getLogger()

router = APIRouter()


@router.get("/me")
async def me(request: Request):
    return {"result": 1, "errorMesage": "", "data": request.scope["client"][0]}


@router.api_route("{route_path:path}", methods=["GET", "POST"])
async def index(request: Request, route_path: str, session: Executor = Depends(db.get_db)):
    method = request.method
    headers = get_headers(request.headers)
    query_params = {
        "workip": request.scope["client"][0],
        "workdt": datetime.now().strftime("%Y%m%d%H%M%S"),
    }
    query_params.update(request.query_params.items())
    data = None
    status = 200
    if method == "POST":
        try:
            data = await request.json()
        except json.JSONDecodeError:
            data = (await request.body()).decode()

    row = session.query(**const.RouteTable.get_query_data(route_path, method)).first()

    if not row:
        logger.error(f"API INFO NOT FOUND, url :: {route_path}, method :: {method}")
        return JSONResponse(
            content={"result": 0, "errorMessage": "API INFO NOT FOUND."},
            status_code=404,
        )

    logger.info(f"API :: {row}")

    remote_url = "http://" + row[const.ROUTE_IP_FIELD] + row[const.ROUTE_API_URL_FIELD]

    cookies, result, status = await request_to_service(remote_url, method, query_params, data, headers)

    response = JSONResponse(content=result, status_code=status)
    if cookies:
        for k, v in cookies.items():
            logger.debug(f"k :: {k} {type(k)}, v :: {v} {type(v)}")
            response.set_cookie(key=k, value=v, domain=v.get("domain"), max_age=3600, secure=False, httponly=False)

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
            return dict(response.cookies), await response.json(), response.status
