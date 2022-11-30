from fastapi.logger import logger
from typing import Dict, List
import importlib.util
from fastapi import APIRouter
from ApiRoute.ApiRouteConfig import config

# from RouterUtils.CommonUtil import connect_db, save_file_for_reload, get_exception_info, delete_headers, kt_lamp  # 함수 내부에 import로 수정
from RouterUtils.RouteUtil import (
    bypass_msg,
    call_remote_func,
    get_api_info,
    make_route_response,
)
from pydantic import BaseModel
from starlette.requests import Request
from urllib import parse
import logging
import uuid


trace_logger = logging.getLogger("trace")


class ApiServerInfo(BaseModel):
    nm: str
    ip_adr: str
    domn_nm: str


class ApiParam(BaseModel):
    api_nm: str
    nm: str
    data_type: str
    deflt_val: str


class ApiInfo(BaseModel):
    api_nm: str
    ctgry: str
    route_url: str
    url: str
    meth: str
    cmd: str
    mode: str
    params: List[ApiParam]


class ApiRoute:
    def __init__(self) -> None:
        self.router = APIRouter()
        self.set_route()

    def set_route(self) -> None:
        from RouterUtils.CommonUtil import connect_db

        self.router.add_api_route(
            "/api/reload", self.reload_api, methods=["GET"], tags=["API Info Reload"]
        )

        db = connect_db()
        config.api_info, _ = db.select("SELECT * FROM api_item_bas;")
        config.api_params, _ = db.select("SELECT * FROM api_item_param_dtl;")

        config.api_server_info, _ = db.select("SELECT * FROM api_item_server_dtl")

        for api in config.api_info:
            method = str(api["mthd"]).split(",")
            self.router.add_api_route(
                api["route_url"],
                self.route_api,
                methods=method,
                tags=[f'Route Category ({api["srvr_nm"]})'],
            )

        for api_name, conf_api_info in config.api_config.items():
            module_name = f'RouterApiList.{conf_api_info["sub_dir"]}.{api_name}'
            spec = importlib.util.find_spec(module_name)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.router.add_api_route(
                f'{conf_api_info["url"]}',
                module.api,
                methods=[conf_api_info["method"]],
                tags=[f'service [ {conf_api_info["sub_dir"]} ]'],
            )

    def reload_api(self):
        from RouterUtils.CommonUtil import save_file_for_reload

        logger.info("Reload API Info")
        save_file_for_reload()
        result = {"result": 1, "errorMessage": ""}
        return result

    async def route_api(self, request: Request) -> Dict:
        # 함수 내부에 import로 수정
        from RouterUtils.CommonUtil import get_exception_info, delete_headers, kt_lamp

        route_url = request.url.path
        method = request.method
        access_token = ""
        body = None
        headers = delete_headers(
            dict(request.headers), ["content-length", "user-agent"]
        )

        transaction_id = f'{config.lamp_info["service_code"]}_{uuid.uuid4()}'
        headers["transactionId"] = transaction_id

        try:
            api_info, api_params = get_api_info(route_url)
            # lamp 1
            kt_lamp("IN_REQ", transaction_id, api_info["api_nm"])

            if method == "POST":
                body = await request.json()

            params_query = parse.unquote(str(request.query_params))

            logger.info(
                f"\n- api_info : {api_info}\n- api_params : {api_params} \
                  \n- req body : {body}, params_query : {params_query}"
            )
            if api_info["mode"] == "MESSAGE PASSING":
                result, access_token = await bypass_msg(
                    api_info, params_query, body, headers
                )
            else:
                result = await call_remote_func(api_info, api_params, body)
        except Exception:
            except_name = get_exception_info()
            result = {"result": 0, "errorMessage": except_name}

        # lamp 6
        kt_lamp("IN_RES", transaction_id, api_info["api_nm"])

        return make_route_response(result, api_info["api_nm"], access_token)
