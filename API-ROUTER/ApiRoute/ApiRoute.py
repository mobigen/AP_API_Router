from fastapi.logger import logger
from typing import Dict, List
import importlib.util
from fastapi import APIRouter
from ApiRoute.ApiRouteConfig import config
from Utils.DataBaseUtil import convert_data
from Utils.CommonUtil import connect_db, make_res_msg, get_user_info, save_file_for_reload
from Utils.RouteUtil import bypass_msg, call_remote_func
from pydantic import BaseModel
from starlette.requests import Request


class ApiServerInfo(BaseModel):
    name: str
    ip_port: str
    domain: str


class ApiParam(BaseModel):
    api_name: str
    param_name: str
    data_type: str
    default_value: str


class ApiInfo(BaseModel):
    api_name: str
    category: str
    url: str
    method: str
    command: str
    bypass: str
    params: List[ApiParam]


class ApiRoute:
    def __init__(self) -> None:
        self.router = APIRouter()
        self.set_route()

    def set_route(self) -> None:
        self.router.add_api_route(
            "/api/getApiList", self.get_api_list, methods=["GET"], tags=["API Info"])
        self.router.add_api_route(
            "/api/getApi", self.get_api, methods=["GET"], tags=["API Info"])
        self.router.add_api_route(
            "/api/setApi", self.set_api, methods=["POST"], tags=["API Info"])
        self.router.add_api_route(
            "/api/delApi", self.del_api, methods=["POST"], tags=["API Info"])

        self.router.add_api_route(
            "/api/getServerInfoList", self.get_server_info_list, methods=["GET"], tags=["API Server Info"])
        self.router.add_api_route(
            "/api/getServerInfo", self.get_server_info, methods=["GET"], tags=["API Server Info"])
        self.router.add_api_route(
            "/api/setServerInfo", self.set_server_info, methods=["POST"], tags=["API Server Info"])
        self.router.add_api_route(
            "/api/delServerInfo", self.del_server_info, methods=["POST"], tags=["API Server Info"])

        db = connect_db(config.db_type, config.db_info)
        api_info, _ = db.select('SELECT * FROM api_info;')

        config.api_server_info, _ = db.select('SELECT * FROM api_server_info')

        for api in api_info:
            self.router.add_api_route(
                f'/route/{api["category"]}/{api["api_name"]}', self.route_api, methods=[api["method"]], tags=[f'Route Category ({api["category"]})'])

        for api_name, api_info in config.api_config.items():
            module_path = f'{config.root_path}/API-ROUTER/ApiList/{api_info["sub_dir"]}/{api_name}.py'
            module_name = "api"
            spec = importlib.util.spec_from_file_location(
                module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.router.add_api_route(f'{api_info["url_prefix"]}/{api_info["sub_dir"]}/{api_name}',
                                      module.api, methods=[api_info["method"]], tags=["service"])

    def set_server_info(self, api_server_info: ApiServerInfo):
        try:
            db = connect_db(config.db_type, config.db_info)
            db.insert("api_server_info", [api_server_info.__dict__])
        except Exception as err:
            result = {"result": 0, "errorMessage": err}
            logger.error(err)
        else:
            config.api_server_info, _ = db.select(
                'SELECT * FROM api_server_info')
            result = {"result": 1, "errorMessage": ""}

        return result

    def get_server_info_list(self):
        try:
            db = connect_db(config.db_type, config.db_info)
            api_server_info, _ = db.select(f'SELECT * FROM api_server_info;')
        except Exception as err:
            result = {"result": 0, "errorMessage": err}
            logger.error(err)
        else:
            result = {"api_server_info": api_server_info}

        return result

    def get_server_info(self, server_name: str):
        try:
            db = connect_db(config.db_type, config.db_info)
            api_server_info, _ = db.select(
                f'SELECT * FROM api_server_info WHERE name = {convert_data(server_name)};')
        except Exception as err:
            result = {"result": 0, "errorMessage": err}
            logger.error(err)
        else:
            result = {"api_server_info": api_server_info}

        return result

    def del_server_info(self, server_name: str):
        try:
            db = connect_db(config.db_type, config.db_info)

            db.delete("api_server_info", {"name": server_name})
        except Exception as err:
            result = {"result": 0, "errorMessage": err}
            logger.error(err)
        else:
            config.api_server_info, _ = db.select(
                'SELECT * FROM api_server_info')
            result = {"result": 1, "errorMessage": ""}

        return result

    def get_api_list(self) -> Dict:
        api_info_query = f'SELECT * FROM api_info;'
        api_params_query = f'SELECT * FROM api_params;'
        try:
            db = connect_db(config.db_type, config.db_info)

            api_info, info_column_names = db.select(api_info_query)
            api_params, params_column_names = db.select(api_params_query)
        except Exception as err:
            result = {"result": 0, "errorMessage": err}
            logger.error(err)
        else:
            api_info = make_res_msg("", "", api_info, info_column_names)
            api_params = make_res_msg("", "", api_params, params_column_names)
            result = {"api_info": api_info, "api_params": api_params}

        return result

    def get_api(self, api_name: str) -> Dict:
        api_info_query = f'SELECT * FROM api_info WHERE api_name = {convert_data(api_name)};'
        api_params_query = f'SELECT * FROM api_params WHERE api_name = {convert_data(api_name)};'
        try:
            db = connect_db(config.db_type, config.db_info)
            api_info, info_column_names = db.select(api_info_query)
            api_params, params_column_names = db.select(api_params_query)
        except Exception as err:
            result = {"result": 0, "errorMessage": err}
            logger.error(err)
        else:
            api_info = make_res_msg("", "", api_info, info_column_names)
            api_params = make_res_msg("", "", api_params, params_column_names)
            result = {"api_info": api_info, "api_params": api_params}

        return result

    def set_api(self, api_info: ApiInfo) -> Dict:
        try:
            db = connect_db(config.db_type, config.db_info)

            insert_api_info = {}
            insert_api_params = []
            for key, value in api_info.__dict__.items():
                if key == "params":
                    for param in value:
                        insert_api_params.append(param.__dict__)
                else:
                    insert_api_info[key] = value

            db.insert("api_info", [insert_api_info])

            if len(insert_api_params) != 0:
                db.insert("api_params", insert_api_params)
        except Exception as err:
            result = {"result": 0, "errorMessage": err}
            logger.error(err)
        else:
            save_file_for_reload()
            result = {"result": 1, "errorMessage": ""}

        return result

    def del_api(self, api_name: str) -> Dict:
        try:
            db = connect_db(config.db_type, config.db_info)

            db.delete("api_info", {"api_name": api_name})
            db.delete("api_params", {"api_name": api_name})
        except Exception as err:
            result = {"result": 0, "errorMessage": err}
            logger.error(err)
        else:
            save_file_for_reload()
            result = {"result": 1, "errorMessage": ""}

        return result

    async def route_api(self, request: Request) -> Dict:
        api_name = request.url.path.split("/")[-1]
        method = request.method
        content_type = request.headers.get("Content-Type")

        user_info = get_user_info(request.headers)

        logger.debug(
            f'Req - API Name : {api_name}, Method : {method}, Content-Type : {content_type}')

        api_info_query = f'SELECT * FROM api_info WHERE api_name = {convert_data(api_name)};'
        api_params_query = f'SELECT * FROM api_params WHERE api_name = {convert_data(api_name)};'

        try:
            db = connect_db(config.db_type, config.db_info)
            api_info, _ = db.select(api_info_query)
            api_params, _ = db.select(api_params_query)
        except Exception as err:
            result = {"result": 0, "errorMessage": err}
            logger.error(err)
        else:
            if len(api_info) == 0:
                return {"result": 0, "errorMessage": "This is an unregistered API."}

            api_info = api_info[0]
            if content_type == "application/json":
                body = await request.json()
                api_info["msg_type"] = "JSON"
            else:
                body = await request.body()
                api_info["msg_type"] = "BINARY"

            params_query = str(request.query_params)

            logger.debug(f'Req - body : {body}, query params : {params_query}')

            logger.debug(f'DB - api_info : {api_info}')
            logger.debug(f'DB - api_params : {api_params}')

            if api_info["bypass"] == "ON":
                result = bypass_msg(api_info, params_query, body)
            else:
                result = call_remote_func(api_info, api_params, body)

        return result
