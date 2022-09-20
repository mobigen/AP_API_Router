from fastapi.logger import logger
from typing import Dict, List
import importlib.util
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from ApiRoute.ApiRouteConfig import config
from Utils.CommonUtil import connect_db, save_file_for_reload, get_exception_info, delete_headers, convert_data
from Utils.RouteUtil import bypass_msg, call_remote_func
from pydantic import BaseModel
from starlette.requests import Request
from urllib import parse


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
            module_path = f'{config.root_path}/ApiList/{api_info["sub_dir"]}/{api_name}.py'
            module_name = "api"
            spec = importlib.util.spec_from_file_location(
                module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.router.add_api_route(f'{api_info["url_prefix"]}/{api_info["sub_dir"]}/{api_name}',
                                      module.api, methods=[api_info["method"]], tags=["service"])

    def reload_api(self):
        logger.info("Reload API Info")
        save_file_for_reload()
        result = {"result": 1, "errorMessage": ""}
        return result

    async def route_api(self, request: Request) -> Dict:
        route_url = request.url.path
        method = request.method
        access_token = ""
        headers = delete_headers(dict(request.headers), [
            "content-length", "user-agent"])
        try:
            db = connect_db()
            api_info, _ = db.select(
                f'SELECT * FROM tb_api_info WHERE route_url = {convert_data(route_url)};')
            api_info = api_info[0]
            api_params, _ = db.select(
                f'SELECT * FROM tb_api_params WHERE api_nm = {convert_data(api_info["api_nm"])};')
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
                result, access_token = await bypass_msg(api_info, params_query, body, headers)
            else:
                result = await call_remote_func(api_info, api_params, body)
        response = JSONResponse(content=result)
        add_cookie_api_list = config.secret_info["add_cookie_api"].split(",")
        if api_info["api_nm"] in add_cookie_api_list:
            response.set_cookie(
                key=config.secret_info["cookie_name"], value=access_token)
        return response
