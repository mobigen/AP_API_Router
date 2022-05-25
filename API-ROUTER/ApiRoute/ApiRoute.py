from fastapi.logger import logger
from typing import Dict, List
import importlib.util
from fastapi import APIRouter
from ApiRoute.ApiRouteConfig import config
from Utils.DataBaseUtil import convert_data
from Utils.CommonUtil import connect_db, make_res_msg, get_token_info, save_file_for_reload
from Utils.RouteUtil import bypass_msg, call_remote_func
from pydantic import BaseModel
from starlette.requests import Request


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
                f'/route/{api["CTGRY"]}/{api["API_NM"]}', self.route_api, methods=[api["METH"]], tags=[f'Route Category ({api["CTGRY"]})'])

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
            api_server_info = api_server_info.__dict__
            api_server_info_query = f'INSERT INTO api_server_info ("NM", "IP_ADR", "DOMN_NM") \
                                            VALUES ({convert_data(api_server_info["nm"])}, {convert_data(api_server_info["ip_adr"])}, {convert_data(api_server_info["domn_nm"])});'
            db.execute(api_server_info_query)
        except Exception as err:
            result = {"result": 0, "errorMessage": err}
            logger.error(err)
        else:
            config.api_server_info, _ = db.select(
                'SELECT * FROM api_server_info;')
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
                f'SELECT * FROM api_server_info WHERE "NM" = {convert_data(server_name)};')
        except Exception as err:
            result = {"result": 0, "errorMessage": err}
            logger.error(err)
        else:
            result = {"api_server_info": api_server_info}

        return result

    def del_server_info(self, server_name: str):
        try:
            db = connect_db(config.db_type, config.db_info)
            api_server_info_query = f'DELETE FROM api_server_info WHERE "NM" = {convert_data(server_name)};'
            db.execute(api_server_info_query)
        except Exception as err:
            result = {"result": 0, "errorMessage": err}
            logger.error(err)
        else:
            config.api_server_info, _ = db.select(
                'SELECT * FROM api_server_info;')
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
        api_info_query = f'SELECT * FROM api_info WHERE "API_NM" = {convert_data(api_name)};'
        api_params_query = f'SELECT * FROM api_params WHERE "API_NM" = {convert_data(api_name)};'
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

            api_info_query = f'INSERT INTO api_info ("API_NM", "CTGRY", "URL", "METH", "CMD", "MODE") \
                                VALUES ({convert_data(insert_api_info["api_nm"])}, {convert_data(insert_api_info["ctgry"])}, {convert_data(insert_api_info["url"])}, \
                                        {convert_data(insert_api_info["meth"])}, {convert_data(insert_api_info["cmd"])}, {convert_data(insert_api_info["mode"])});'
            db.execute(api_info_query)

            if len(insert_api_params) != 0:
                api_params_query = f'INSERT INTO api_params ("API_NM", "NM", "DATA_TYPE", "DEFLT_VAL") \
                                            VALUES ({convert_data(insert_api_params["api_nm"])}, {convert_data(insert_api_params["nm"])}, \
                                                    {convert_data(insert_api_params["data_type"])}, {convert_data(insert_api_params["deflt_val"])});'
                db.execute(api_params_query)
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

            api_info_query = f'DELETE FROM api_info WHERE "API_NM" = {convert_data(api_name)};'
            db.execute(api_info_query)
            api_params_query = f'DELETE FROM api_params WHERE  "API_NM" = {convert_data(api_name)};'
            db.execute(api_params_query)
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

        user_info = get_token_info(request.headers)

        logger.debug(
            f'Req - API Name : {api_name}, Method : {method}, Content-Type : {content_type}')

        api_info_query = f'SELECT * FROM api_info WHERE "API_NM" = {convert_data(api_name)};'
        api_params_query = f'SELECT * FROM api_params WHERE "API_NM" = {convert_data(api_name)};'

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
                api_info["MSG_TYPE"] = "JSON"
            else:
                body = await request.body()
                api_info["MSG_TYPE"] = "BINARY"

            params_query = str(request.query_params)

            logger.debug(f'Req - body : {body}, query params : {params_query}')

            logger.debug(f'DB - api_info : {api_info}')
            logger.debug(f'DB - api_params : {api_params}')

            logger.error(f'MODE : {api_info["MODE"]}, content_type : {content_type}')
            #if api_info["MODE"] == "MESSAGE PASSING":
            result = bypass_msg(api_info, params_query, body)
            #else:
            #    result = call_remote_func(api_info, api_params, body)

        return result
