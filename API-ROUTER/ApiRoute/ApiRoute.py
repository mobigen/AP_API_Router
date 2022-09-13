from fastapi.logger import logger
from typing import Dict, List
import importlib.util
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from ApiRoute.ApiRouteConfig import config
from Utils.DataBaseUtil import convert_data
from Utils.CommonUtil import connect_db, make_res_msg, save_file_for_reload, get_exception_info, delete_headers
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

    def set_server_info(self, api_server_info: ApiServerInfo) -> Dict:
        api_server_info = api_server_info.__dict__
        api_server_info_query = f'INSERT INTO tb_api_server_info (nm, ip_adr, domn_nm) \
                                        VALUES ({convert_data(api_server_info["nm"])}, \
                                                {convert_data(api_server_info["ip_adr"])}, \
                                                {convert_data(api_server_info["domn_nm"])});'
        try:
            db = connect_db()
            db.execute(api_server_info_query)
        except Exception:
            except_name = get_exception_info()
            result = {"result": 0, "errorMessage": except_name}
        else:
            config.api_server_info, _ = db.select(
                'SELECT * FROM tb_api_server_info;')
            result = {"result": 1, "errorMessage": ""}

        return result

    def update_server_info(self, api_server_info: ApiServerInfo) -> Dict:
        api_server_info = api_server_info.__dict__
        api_server_info_query = f'UPDATE tb_api_server_info SET ip_adr={convert_data(api_server_info["ip_adr"])}, \
                                                             domn_nm={convert_data(api_server_info["domn_nm"])} \
                                                         WHERE nm={convert_data(api_server_info["nm"])};'
        try:
            db = connect_db()
            db.execute(api_server_info_query)
        except Exception:
            except_name = get_exception_info()
            result = {"result": 0, "errorMessage": except_name}
        else:
            config.api_server_info, _ = db.select(
                'SELECT * FROM tb_api_server_info;')
            result = {"result": 1, "errorMessage": ""}

        return result

    def get_server_info_list(self) -> Dict:
        try:
            db = connect_db()
            api_server_info, _ = db.select(
                'SELECT * FROM tb_api_server_info ORDER BY nm;')
        except Exception:
            except_name = get_exception_info()
            result = {"result": 0, "errorMessage": except_name}
        else:
            result = {"api_server_info": api_server_info}

        return result

    def get_server_info(self, nm: str) -> Dict:
        try:
            db = connect_db()
            api_server_info, _ = db.select(
                f'SELECT * FROM tb_api_server_info WHERE nm = {convert_data(nm)};')
        except Exception:
            except_name = get_exception_info()
            result = {"result": 0, "errorMessage": except_name}
        else:
            result = {"api_server_info": api_server_info}

        return result

    def del_server_info(self, nm: str) -> Dict:
        try:
            db = connect_db()
            db.execute(
                f'DELETE FROM tb_api_server_info WHERE nm = {convert_data(nm)};')
        except Exception:
            except_name = get_exception_info()
            result = {"result": 0, "errorMessage": except_name}
        else:
            config.api_server_info, _ = db.select(
                'SELECT * FROM tb_api_server_info;')
            result = {"result": 1, "errorMessage": ""}

        return result

    def reload_api(self):
        logger.info("Reload API Info")
        save_file_for_reload()
        result = {"result": 1, "errorMessage": ""}
        return result

    def get_api_list(self) -> Dict:
        try:
            db = connect_db()

            api_info, info_column_names = db.select(
                f'SELECT api_nm, ctgry, route_url, url, meth, cmd, mode FROM tb_api_info;')
            api_params, params_column_names = db.select(
                f'SELECT * FROM tb_api_params ORDER BY api_nm, nm;')
        except Exception:
            except_name = get_exception_info()
            result = {"result": 0, "errorMessage": except_name}
        else:
            api_info = make_res_msg("", "", api_info, info_column_names)
            api_params = make_res_msg("", "", api_params, params_column_names)
            result = {"api_info": api_info, "api_params": api_params}

        return result

    def get_api_category_list(self, ctgry: str) -> Dict:
        api_params_list = []
        params_columns = []
        try:
            db = connect_db()
            api_info, info_column_names = db.select(
                f'SELECT api_nm, ctgry, route_url, url, meth, cmd, mode FROM tb_api_info WHERE ctgry = {convert_data(ctgry)};')

            for info in api_info:
                logger.info(f'INFO : {info["api_nm"]}')
                api_params, params_column_names = db.select(
                    f'SELECT * FROM tb_api_params WHERE api_nm = {convert_data(info["api_nm"])} ORDER BY nm;')
                if len(api_params) != 0:
                    api_params_list.extend(api_params)
                    params_columns = params_column_names
        except Exception:
            except_name = get_exception_info()
            result = {"result": 0, "errorMessage": except_name}
        else:
            api_info = make_res_msg("", "", api_info, info_column_names)
            api_params = make_res_msg(
                "", "", api_params_list, params_columns)
            result = {"api_info": api_info, "api_params": api_params}

        return result

    def get_api(self, api_nm: str) -> Dict:
        try:
            db = connect_db()
            api_info, info_column_names = db.select(
                f'SELECT * FROM tb_api_info WHERE api_nm = {convert_data(api_nm)};')
            api_params, params_column_names = db.select(
                f'SELECT * FROM tb_api_params WHERE api_nm = {convert_data(api_nm)} ORDER BY nm;')
        except Exception:
            except_name = get_exception_info()
            result = {"result": 0, "errorMessage": except_name}
        else:
            api_info = make_res_msg("", "", api_info, info_column_names)
            api_params = make_res_msg("", "", api_params, params_column_names)
            result = {"api_info": api_info, "api_params": api_params}

        return result

    def set_api(self, api_info: ApiInfo) -> Dict:
        try:
            db = connect_db()

            insert_api_info = {}
            insert_api_params = []
            for key, value in api_info.__dict__.items():
                if key == "params":
                    for param in value:
                        insert_api_params.append(param.__dict__)
                else:
                    insert_api_info[key] = value

            api_info_query = f'INSERT INTO tb_api_info (api_nm, ctgry, route_url, url, meth, cmd, mode) \
                                      VALUES ({convert_data(insert_api_info["api_nm"])}, {convert_data(insert_api_info["ctgry"])}, \
                                              {convert_data(insert_api_info["route_url"])}, {convert_data(insert_api_info["url"])}, \
                                              {convert_data(insert_api_info["meth"])}, {convert_data(insert_api_info["cmd"])}, \
                                              {convert_data(insert_api_info["mode"])});'
            db.execute(api_info_query)

            for param in insert_api_params:
                api_params_query = f'INSERT INTO tb_api_params (api_nm, nm, data_type, deflt_val) \
                                            VALUES ({convert_data(param["api_nm"])}, {convert_data(param["nm"])}, \
                                                    {convert_data(param["data_type"])}, {convert_data(param["deflt_val"])});'
                db.execute(api_params_query)
        except Exception:
            except_name = get_exception_info()
            result = {"result": 0, "errorMessage": except_name}
        else:
            save_file_for_reload()
            result = {"result": 1, "errorMessage": ""}

        return result

    def update_api(self, api_info: ApiInfo) -> Dict:
        try:
            db = connect_db()

            insert_api_info = {}
            insert_api_params = []
            for key, value in api_info.__dict__.items():
                if key == "params":
                    for param in value:
                        insert_api_params.append(param.__dict__)
                else:
                    insert_api_info[key] = value
            db.execute(
                f'DELETE FROM tb_api_info WHERE api_nm = {convert_data(insert_api_info["api_nm"])};')

            api_info_query = f'INSERT INTO tb_api_info (api_nm, ctgry, route_url, url, meth, cmd, mode) \
                                      VALUES ({convert_data(insert_api_info["api_nm"])}, {convert_data(insert_api_info["ctgry"])}, \
                                              {convert_data(insert_api_info["route_url"])}, {convert_data(insert_api_info["url"])}, \
                                              {convert_data(insert_api_info["meth"])}, {convert_data(insert_api_info["cmd"])}, \
                                              {convert_data(insert_api_info["mode"])});'

            db.execute(api_info_query)

            for param in insert_api_params:
                api_params_query = f'INSERT INTO tb_api_params (api_nm, nm, data_type, deflt_val) \
                                            VALUES ({convert_data(param["api_nm"])}, {convert_data(param["nm"])}, \
                                                    {convert_data(param["data_type"])}, {convert_data(param["deflt_val"])});'
                db.execute(api_params_query)

        except Exception:
            except_name = get_exception_info()
            result = {"result": 0, "errorMessage": except_name}
        else:
            save_file_for_reload()
            result = {"result": 1, "errorMessage": ""}

        return result

    def del_api(self, api_nm: str) -> Dict:
        try:
            db = connect_db()
            db.execute(
                f'DELETE FROM tb_api_info WHERE api_nm = {convert_data(api_nm)};')
        except Exception:
            except_name = get_exception_info()
            result = {"result": 0, "errorMessage": except_name}
        else:
            save_file_for_reload()
            result = {"result": 1, "errorMessage": ""}

        return result

    async def route_api(self, request: Request) -> Dict:
        route_url = request.url.path
        method = request.method
        req_access_token = request.headers.get(
            config.secret_info["header_name"])
        res_access_token = None
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
        except Exception:
            except_name = get_exception_info()
            result = {"result": 0, "errorMessage": except_name}
        else:
            if len(api_info) == 0:
                return {"result": 0, "errorMessage": "This is an unregistered API."}

            body = None
            if method == "POST":
                body = await request.json()

            params_query = parse.unquote(str(request.query_params))
            logger.info(
                f'Req - body : {body}, query params : {params_query}')

            api_info["meth"] = method
            logger.info(f'DB - api_info : {api_info}')
            logger.info(f'DB - api_params : {api_params}')

            logger.info(f'mode : {api_info["mode"]}')
            if api_info["mode"] == "MESSAGE PASSING":
                result, res_access_token = await bypass_msg(api_info, params_query, body, headers)
            else:
                result = await call_remote_func(api_info, api_params, body)

            remove_header_api_list = config.secret_info["remove_header_api"].split(
                ",")

            if api_info["api_nm"] not in remove_header_api_list:
                if res_access_token is None:
                    if req_access_token is not None:
                        access_token = req_access_token
                else:
                    access_token = res_access_token

            logger.info(f'access token : {access_token}')
        return JSONResponse(content=result, headers={config.secret_info["header_name"]: access_token})
