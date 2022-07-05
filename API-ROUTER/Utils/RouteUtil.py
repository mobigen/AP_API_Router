import asyncssh
import aiohttp
from fastapi.logger import logger
from urllib.parse import ParseResult
from ApiRoute.ApiRouteConfig import config
from typing import Dict


def make_url(server_name: str, url_path: str):
    for server_info in config.api_server_info:
        if server_info["nm"] == server_name:
            if len(server_info["ip_adr"]) != 0:
                netloc = server_info["ip_adr"]
            else:
                netloc = server_info["domn_nm"]
            url = ParseResult(
                scheme="http", netloc=netloc, path=url_path, params="", query="", fragment="")
            logger.info(f"Message Passing Url : {url.geturl()}")
            return url.geturl()
    return None


async def bypass_msg(api_info, params_query, body, headers):
    method = api_info["meth"]
    msg_type = api_info["msg_type"]

    url = make_url(api_info["ctgry"], api_info["url"])
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
                result = await response.json()
        elif method == "POST":
            if msg_type == "JSON":
                async with session.post(url, json=body, headers=headers) as response:
                    result = await response.json()
            else:
                async with session.post(url, data=body, headers=headers) as response:
                    result = await response.json()
        else:
            logger.error(f'Method Not Allowed. {method}')
            result = {"result": 0, "errorMessage": "Method Not Allowed."}
    return result


async def run_cmd(cmd: str):
    async with asyncssh.connect(host=config.remote_info["host"], port=int(config.remote_info["port"]),
                                username=config.remote_info["id"], password=config.remote_info["password"]) as conn:
        result = await conn.run(cmd, check=True)
        logger.info(f'Command Result : {result.stdout}')
    return result.stdout


async def call_remote_func(api_info, api_params, input_params) -> Dict:
    msg_type = api_info["msg_type"]

    command_input = ""
    if msg_type == "JSON":
        for param in api_params:
            try:
                data = input_params[param["param_name"]]
                command_input += f' --{param["param_name"]} {data}'
            except KeyError:
                logger.error(
                    f'parameter set default value. [{param["param_name"]}]')
                command_input += f' --{param["param_name"]} {param["default_value"]}'

    cmd = f'{api_info["cmd"]} {command_input}'

    try:
        result = await run_cmd(cmd)
    except (OSError, asyncssh.Error) as exc:
        logger.error(f'SSH connection failed: {str(exc)}')

    return eval(result)
