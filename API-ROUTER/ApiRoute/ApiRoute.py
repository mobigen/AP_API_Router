from fastapi.logger import logger
from typing import Dict, List
import importlib.util
from fastapi import APIRouter
from ApiRoute.ApiRouteConfig import config
from RouterUtils.CommonUtil import connect_db, make_res_msg, save_file_for_reload, get_exception_info, delete_headers, convert_data
from RouterUtils.RouteUtil import bypass_msg, call_remote_func
from pydantic import BaseModel
from starlette.requests import Request
from urllib import parse
import logging

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
        self.router.add_api_route(
            "/api/reload", self.reload_api, methods=["GET"], tags=["API Info Reload"])

        db = connect_db()
        api_info, _ = db.select('SELECT * FROM api_item_bas;')

        config.api_server_info, _ = db.select(
            'SELECT * FROM api_item_server_dtl')

        for api in api_info:
            method = str(api["mthd"]).split(",")
            self.router.add_api_route(
                api["route_url"], self.route_api, methods=method, tags=[f'Route Category ({api["srvr_nm"]})'])

        for api_name, conf_api_info in config.api_config.items():
            module_name = f'RouterApiList.{conf_api_info["sub_dir"]}.{api_name}'
            spec = importlib.util.find_spec(module_name)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.router.add_api_route(f'{conf_api_info["url"]}',
                                      module.api, methods=[
                                          conf_api_info["method"]],
                                      tags=[f'service [ {conf_api_info["sub_dir"]} ]'])

    def reload_api(self):
        logger.info("Reload API Info")
        save_file_for_reload()
        result = {"result": 1, "errorMessage": ""}
        return result


    async def route_api(self, request: Request) -> Dict:
        route_url = request.url.path
        method = request.method
        headers = delete_headers(dict(request.headers), [
            "content-length", "user-agent"])
        try:
            db = connect_db()
            api_info, _ = db.select(
                f'SELECT * FROM api_item_bas WHERE route_url = {convert_data(route_url)};')
            api_info = api_info[0]
            api_params, _ = db.select(
                f'SELECT * FROM api_item_param_dtl WHERE api_nm = {convert_data(api_info["api_nm"])};')
            logger.info(
                f'\nDB - api_info : {api_info}\nDB - api_params : {api_params}')
        except Exception:
            except_name = get_exception_info()
            result = {"result": 0, "errorMessage": except_name}
        else:
            if method == "POST":
                body = await request.json()
            else:
                body = None
            params_query = parse.unquote(str(request.query_params))

            logger.info(
                f'\nReq - body : {body}\nquery params : {params_query}')

            if api_info["mode"] == "MESSAGE PASSING":
                result = await bypass_msg(api_info, params_query, body, headers)
            else:
                result = await call_remote_func(api_info, api_params, body)
        return result
