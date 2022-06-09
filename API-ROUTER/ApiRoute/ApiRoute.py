from fastapi.logger import logger
from typing import Dict, List
import importlib.util
from fastapi import APIRouter
from ApiRoute.ApiRouteConfig import config
from Utils.DataBaseUtil import convert_data
from Utils.CommonUtil import connect_db, make_res_msg, get_token_info, save_file_for_reload, get_exception_info
from Utils.RouteUtil import bypass_msg, call_remote_func
from pydantic import BaseModel
from starlette.requests import Request


class ApiServerInfo(BaseModel):
    NM: str
    IP_ADR: str
    DOMN_NM: str


class ApiParam(BaseModel):
    API_NM: str
    NM: str
    DATA_TYPE: str
    DEFLT_VAL: str


class ApiInfo(BaseModel):
    API_NM: str
    CTGRY: str
    URL: str
    METH: str
    CMD: str
    MODE: str
    PARAMS: List[ApiParam]


class ApiRoute:
    def __init__(self) -> None:
        self.router = APIRouter()
        self.set_route()

    def set_route(self) -> None:
        self.router.add_api_route(
            "/api/getApiList", self.get_api_list, methods=["GET"], tags=["API Info"])
        self.router.add_api_route(
            "/api/getCategoryApiList", self.get_api_category_list, methods=["GET"], tags=["API Info"])
        self.router.add_api_route(
            "/api/getApi", self.get_api, methods=["GET"], tags=["API Info"])
        self.router.add_api_route(
            "/api/setApi", self.set_api, methods=["POST"], tags=["API Info"])
        self.router.add_api_route(
            "/api/updateApi", self.update_api, methods=["POST"], tags=["API Info"])
        self.router.add_api_route(
            "/api/delApi", self.del_api, methods=["POST"], tags=["API Info"])

        self.router.add_api_route(
            "/api/getServerInfoList", self.get_server_info_list, methods=["GET"], tags=["API Server Info"])
        self.router.add_api_route(
            "/api/getServerInfo", self.get_server_info, methods=["GET"], tags=["API Server Info"])
        self.router.add_api_route(
            "/api/setServerInfo", self.set_server_info, methods=["POST"], tags=["API Server Info"])
        self.router.add_api_route(
            "/api/updateServerInfo", self.update_server_info, methods=["POST"], tags=["API Server Info"])
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
        api_server_info = api_server_info.__dict__
        api_server_info_query = f'INSERT INTO api_server_info ("NM", "IP_ADR", "DOMN_NM") \
                                        VALUES ({convert_data(api_server_info["NM"])}, \
                                                {convert_data(api_server_info["IP_ADR"])}, \
                                                {convert_data(api_server_info["DOMN_NM"])});'
        try:
            db = connect_db(config.db_type, config.db_info)
            db.execute(api_server_info_query)
        except Exception:
            ex_type, ex_value, trace_log = get_exception_info()
            logger.error("Exception type : {}\nException message : {}\nTrace Log : {}"
                         .format(ex_type, str(ex_value).strip(), trace_log))
            result = {"result": 0, "errorMessage": ex_type}
        else:
            config.api_server_info, _ = db.select(
                'SELECT * FROM api_server_info;')
            result = {"result": 1, "errorMessage": ""}

        return result

    def update_server_info(self, api_server_info: ApiServerInfo):
        api_server_info = api_server_info.__dict__
        api_server_info_query = f'UPDATE api_server_info SET "IP_ADR"={convert_data(api_server_info["IP_ADR"])}, \
                                                             "DOMN_NM"={convert_data(api_server_info["DOMN_NM"])} \
                                                         WHERE "NM"={convert_data(api_server_info["NM"])};'
        try:
            db = connect_db(config.db_type, config.db_info)
            db.execute(api_server_info_query)
        except Exception:
            ex_type, ex_value, trace_log = get_exception_info()
            logger.error("Exception type : {}\nException message : {}\nTrace Log : {}"
                         .format(ex_type, str(ex_value).strip(), trace_log))
            result = {"result": 0, "errorMessage": ex_type}
        else:
            config.api_server_info, _ = db.select(
                'SELECT * FROM api_server_info;')
            result = {"result": 1, "errorMessage": ""}

        return result

    def get_server_info_list(self):
        try:
            db = connect_db(config.db_type, config.db_info)
            api_server_info, _ = db.select(
                'SELECT * FROM api_server_info ORDER BY "NM";')
        except Exception:
            ex_type, ex_value, trace_log = get_exception_info()
            logger.error("Exception type : {}\nException message : {}\nTrace Log : {}"
                         .format(ex_type, str(ex_value).strip(), trace_log))
            result = {"result": 0, "errorMessage": ex_type}
        else:
            result = {"api_server_info": api_server_info}

        return result

    def get_server_info(self, NM: str):
        try:
            db = connect_db(config.db_type, config.db_info)
            api_server_info, _ = db.select(
                f'SELECT * FROM api_server_info WHERE "NM" = {convert_data(NM)};')
        except Exception:
            ex_type, ex_value, trace_log = get_exception_info()
            logger.error("Exception type : {}\nException message : {}\nTrace Log : {}"
                         .format(ex_type, str(ex_value).strip(), trace_log))
            result = {"result": 0, "errorMessage": ex_type}
        else:
            result = {"api_server_info": api_server_info}

        return result

    def del_server_info(self, NM: str):
        try:
            db = connect_db(config.db_type, config.db_info)
            db.execute(
                f'DELETE FROM api_server_info WHERE "NM" = {convert_data(NM)};')
        except Exception:
            ex_type, ex_value, trace_log = get_exception_info()
            logger.error("Exception type : {}\nException message : {}\nTrace Log : {}"
                         .format(ex_type, str(ex_value).strip(), trace_log))
            result = {"result": 0, "errorMessage": ex_type}
        else:
            config.api_server_info, _ = db.select(
                'SELECT * FROM api_server_info;')
            result = {"result": 1, "errorMessage": ""}

        return result

    def get_api_list(self) -> Dict:
        try:
            db = connect_db(config.db_type, config.db_info)

            api_info, info_column_names = db.select(
                f'SELECT "API_NM", "CTGRY", "URL", "METH", "CMD", "MODE" FROM api_info ORDER BY "NO";')
            api_params, params_column_names = db.select(
                f'SELECT * FROM api_params ORDER BY "API_NM", "NM";')
        except Exception:
            ex_type, ex_value, trace_log = get_exception_info()
            logger.error("Exception type : {}\nException message : {}\nTrace Log : {}"
                         .format(ex_type, str(ex_value).strip(), trace_log))
            result = {"result": 0, "errorMessage": ex_type}
        else:
            api_info = make_res_msg("", "", api_info, info_column_names)
            api_params = make_res_msg("", "", api_params, params_column_names)
            result = {"api_info": api_info, "api_params": api_params}

        return result

    def get_api_category_list(self, CTGRY: str):
        api_params_list = []
        params_columns = []
        try:
            db = connect_db(config.db_type, config.db_info)
            api_info, info_column_names = db.select(
                f'SELECT "API_NM", "CTGRY", "URL", "METH", "CMD", "MODE" FROM api_info WHERE "CTGRY" = {convert_data(CTGRY)} ORDER BY "NO";')

            for info in api_info:
                logger.debug(f'INFO : {info["API_NM"]}')
                api_params, params_column_names = db.select(
                    f'SELECT * FROM api_params WHERE "API_NM" = {convert_data(info["API_NM"])} ORDER BY "NM";')
                if len(api_params) != 0:
                    api_params_list.extend(api_params)
                    params_columns = params_column_names
        except Exception:
            ex_type, ex_value, trace_log = get_exception_info()
            logger.error("Exception type : {}\nException message : {}\nTrace Log : {}"
                         .format(ex_type, str(ex_value).strip(), trace_log))
            result = {"result": 0, "errorMessage": ex_type}
        else:
            api_info = make_res_msg("", "", api_info, info_column_names)
            api_params = make_res_msg(
                "", "", api_params_list, params_columns)
            result = {"api_info": api_info, "api_params": api_params}

        return result

    def get_api(self, API_NM: str) -> Dict:
        try:
            db = connect_db(config.db_type, config.db_info)
            api_info, info_column_names = db.select(
                f'SELECT * FROM api_info WHERE "API_NM" = {convert_data(API_NM)};')
            api_params, params_column_names = db.select(
                f'SELECT * FROM api_params WHERE "API_NM" = {convert_data(API_NM)} ORDER BY "NM";')
        except Exception:
            ex_type, ex_value, trace_log = get_exception_info()
            logger.error("Exception type : {}\nException message : {}\nTrace Log : {}"
                         .format(ex_type, str(ex_value).strip(), trace_log))
            result = {"result": 0, "errorMessage": ex_type}
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
                if key == "PARAMS":
                    for param in value:
                        insert_api_params.append(param.__dict__)
                else:
                    insert_api_info[key] = value

            api_info_query = f'INSERT INTO api_info ("API_NM", "CTGRY", "URL", "METH", "CMD", "MODE") \
                                      VALUES ({convert_data(insert_api_info["API_NM"])}, {convert_data(insert_api_info["CTGRY"])}, \
                                              {convert_data(insert_api_info["URL"])}, {convert_data(insert_api_info["METH"])}, \
                                              {convert_data(insert_api_info["CMD"])}, {convert_data(insert_api_info["MODE"])});'
            db.execute(api_info_query)

            for param in insert_api_params:
                api_params_query = f'INSERT INTO api_params ("API_NM", "NM", "DATA_TYPE", "DEFLT_VAL") \
                                            VALUES ({convert_data(param["API_NM"])}, {convert_data(param["NM"])}, \
                                                    {convert_data(param["DATA_TYPE"])}, {convert_data(param["DEFLT_VAL"])});'
                db.execute(api_params_query)
        except Exception:
            ex_type, ex_value, trace_log = get_exception_info()
            logger.error("Exception type : {}\nException message : {}\nTrace Log : {}"
                         .format(ex_type, str(ex_value).strip(), trace_log))
            result = {"result": 0, "errorMessage": ex_type}
        else:
            save_file_for_reload()
            result = {"result": 1, "errorMessage": ""}

        return result

    def update_api(self, api_info: ApiInfo):
        try:
            db = connect_db(config.db_type, config.db_info)

            insert_api_info = {}
            insert_api_params = []
            for key, value in api_info.__dict__.items():
                if key == "PARAMS":
                    for param in value:
                        insert_api_params.append(param.__dict__)
                else:
                    insert_api_info[key] = value
            db.execute(
                f'DELETE FROM api_info WHERE "API_NM" = {convert_data(insert_api_info["API_NM"])};')

            api_info_query = f'INSERT INTO api_info ("API_NM", "CTGRY", "URL", "METH", "CMD", "MODE") \
                                      VALUES ({convert_data(insert_api_info["API_NM"])}, {convert_data(insert_api_info["CTGRY"])}, \
                                              {convert_data(insert_api_info["URL"])}, {convert_data(insert_api_info["METH"])}, \
                                              {convert_data(insert_api_info["CMD"])}, {convert_data(insert_api_info["MODE"])});'
            db.execute(api_info_query)

            for param in insert_api_params:
                api_params_query = f'INSERT INTO api_params ("API_NM", "NM", "DATA_TYPE", "DEFLT_VAL") \
                                            VALUES ({convert_data(param["API_NM"])}, {convert_data(param["NM"])}, \
                                                    {convert_data(param["DATA_TYPE"])}, {convert_data(param["DEFLT_VAL"])});'
                db.execute(api_params_query)

        except Exception:
            ex_type, ex_value, trace_log = get_exception_info()
            logger.error("Exception type : {}\nException message : {}\nTrace Log : {}"
                         .format(ex_type, str(ex_value).strip(), trace_log))
            result = {"result": 0, "errorMessage": ex_type}
        else:
            save_file_for_reload()
            result = {"result": 1, "errorMessage": ""}

        return result

    def del_api(self, API_NM: str) -> Dict:
        try:
            db = connect_db(config.db_type, config.db_info)

            db.execute(
                f'DELETE FROM api_info WHERE "API_NM" = {convert_data(API_NM)};')

        except Exception:
            ex_type, ex_value, trace_log = get_exception_info()
            logger.error("Exception type : {}\nException message : {}\nTrace Log : {}"
                         .format(ex_type, str(ex_value).strip(), trace_log))
            result = {"result": 0, "errorMessage": ex_type}
        else:
            save_file_for_reload()
            result = {"result": 1, "errorMessage": ""}

        return result

    async def route_api(self, request: Request) -> Dict:
        api_name = request.url.path.split("/")[-1]
        category = request.url.path.split("/")[-2]
        method = request.method
        content_type = request.headers.get("Content-Type")

        user_info = get_token_info(request.headers)

        logger.debug(
            f'Req - API Name : {api_name}, Category : {category}, Method : {method}, Content-Type : {content_type}')
        try:
            db = connect_db(config.db_type, config.db_info)
            api_info, _ = db.select(
                f'SELECT * FROM api_info WHERE "API_NM" = {convert_data(api_name)} AND "CTGRY" = {convert_data(category)};')
            api_params, _ = db.select(
                f'SELECT * FROM api_params WHERE "API_NM" = {convert_data(api_name)};')
        except Exception:
            ex_type, ex_value, trace_log = get_exception_info()
            logger.error("Exception type : {}\nException message : {}\nTrace Log : {}"
                         .format(ex_type, str(ex_value).strip(), trace_log))
            result = {"result": 0, "errorMessage": ex_type}
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

            logger.debug(
                f'MODE : {api_info["MODE"]}, content_type : {content_type}')
            if api_info["MODE"] == "MESSAGE PASSING":
                result = await bypass_msg(api_info, params_query, body)
            else:
                result = await call_remote_func(api_info, api_params, body)
        return result
