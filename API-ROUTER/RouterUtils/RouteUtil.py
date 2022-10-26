import asyncssh
import aiohttp
from fastapi.logger import logger
from fastapi.responses import JSONResponse
from urllib.parse import ParseResult
from ApiRoute.ApiRouteConfig import config
from RouterUtils.CommonUtil import get_exception_info
from typing import Dict


def make_url(server_name: str, url_path: str):
    for server_info in config.api_server_info:
        if server_info["srvr_nm"] == server_name:
            if len(server_info["ip_adr"]) != 0:
                netloc = server_info["ip_adr"]
            else:
                netloc = server_info["domn_nm"]
            url = ParseResult(
                scheme="http", netloc=netloc, path=url_path, params="", query="", fragment="")
            logger.info(f"Message Passing Url : {url.geturl()}")
            return url.geturl()
    return None


def make_route_response(result, api_name, access_token):
    response = JSONResponse(content=result)
    add_cookie_api_list = config.secret_info["add_cookie_api"].split(",")
    if api_name in add_cookie_api_list:
        response.set_cookie(
            key=config.secret_info["cookie_name"], value=access_token, max_age=3600, secure=False, httponly=True)
    return response


def get_api_info(route_url):
    api_info = None
    api_params = None
    for api in config.api_info:
        if api["route_url"] == route_url:
            api_info = api
            for params in config.api_params:
                if params["api_nm"] == api["api_nm"]:
                    api_params = params
                    break
            break
    return api_info, api_params


async def bypass_msg(api_info, params_query, body, headers):
    method = api_info["mthd"]

    url = make_url(api_info["srvr_nm"], api_info["url"])
    if url is None:
        return {"result": 0, "errorMessage": "The server info does not exist."}

    async with aiohttp.ClientSession() as session:
        if method == "GET":
            params = {}
            if len(params_query) != 0:
                for param in params_query.split("&"):
                    parser_param = param.split("=")
                    params[parser_param[0]] = parser_param[1]

            async with session.get(url, params=params, headers=headers) as response:
                access_token = response.cookies.get(
                    config.secret_info["cookie_name"])
                result = await response.json()
        elif method == "POST":
            async with session.post(url, json=body, headers=headers) as response:
                access_token = response.cookies.get(
                    config.secret_info["cookie_name"])
                result = await response.json()
        else:
            logger.error(f'Method Not Allowed. {method}')
            result = {"result": 0, "errorMessage": "Method Not Allowed."}
    return result, access_token


async def run_cmd(cmd: str):
    async with asyncssh.connect(host=config.remote_info["host"], port=int(config.remote_info["port"]),
                                username=config.remote_info["id"], password=config.remote_info["password"], known_hosts=None) as conn:
        logger.info(f'Run Cmd : {cmd}')
        result = await conn.run(cmd, check=True)
        logger.info(f'Command Result : {result.stdout}')
    return result.stdout


async def call_remote_func(api_info, api_params, input_params) -> Dict:
    command_input = ""
    try:
        data = input_params[api_params["nm"]]
        if not data:
            data = api_params["deflt_val"]
        command_input += f' --{api_params["nm"]} {data}'
    except KeyError:
        logger.error(
            f'parameter set default value. [{api_params["nm"]}]')
        command_input += f' --{api_params["nm"]} {api_params["deflt_val"]}'

    cmd = f'{api_info["cmd"]} {command_input}'

    try:
        result = await run_cmd(cmd)
    except Exception:
        except_name = get_exception_info()
        res_msg = {"result": 0, "errorMessage": except_name}
    else:
        res_msg = {"result": 1, "errorMessage": "", "data": eval(result)}
    return res_msg
