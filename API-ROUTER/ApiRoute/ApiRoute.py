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
        api_info, _ = db.select('SELECT * FROM tb_api_info;')

        config.api_server_info, _ = db.select(
            'SELECT * FROM tb_api_server_info')

        for api in api_info:
            method = str(api["meth"]).split(",")
            self.router.add_api_route(
                api["route_url"], self.route_api, methods=method, tags=[f'Route Category ({api["ctgry"]})'])

        for api_name, api_info in config.api_config.items():
            module_name = f'RouterApiList.{api_info["sub_dir"]}.{api_name}'
            spec = importlib.util.find_spec(module_name)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.router.add_api_route(f'{api_info["url"]}',
                                      module.api, methods=[
                                          api_info["method"]],
                                      tags=[f'service [ {api_info["sub_dir"]} ]'])

    def reload_api(self):
        logger.info("Reload API Info")
        save_file_for_reload()
        result = {"result": 1, "errorMessage": ""}
        return result

    async def route_api(self, request: Request) -> Dict:
        route_url = request.url.path
        method = request.method
        content_type = request.headers.get("Content-Type")

        logger.info(f"Origin Req Headers : {dict(request.headers)}")
        headers = delete_headers(dict(request.headers), [
                                 "content-length", "user-agent"])
        logger.info(f'Modify Req Headers : {headers}')

        try:
            db = connect_db()
            api_info, _ = db.select(
                f'SELECT * FROM tb_api_info WHERE route_url = {convert_data(route_url)};')
            api_info = api_info[0]
            api_params, _ = db.select(
                f'SELECT * FROM tb_api_params WHERE api_nm = {convert_data(api_info["api_nm"])};')
        except Exception:
            except_name = get_exception_info()
            result = {"result": 0, "errorMessage": except_name}
        else:
            if len(api_info) == 0:
                return {"result": 0, "errorMessage": "This is an unregistered API."}

            if content_type == "application/json":
                body = await request.json()
                api_info["msg_type"] = "JSON"
            else:
                body = await request.body()
                api_info["msg_type"] = "BINARY"

            params_query = parse.unquote(str(request.query_params))
            logger.info(
                f'Req - body : {body}, query params : {params_query}')

            api_info["meth"] = method
            logger.info(f'DB - api_info : {api_info}')
            logger.info(f'DB - api_params : {api_params}')

            logger.info(
                f'mode : {api_info["mode"]}, content_type : {content_type}')
            if api_info["mode"] == "MESSAGE PASSING":
                result = await bypass_msg(api_info, params_query, body, headers)
            else:
                result = await call_remote_func(api_info, api_params, body)
        return result
