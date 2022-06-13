import asyncssh
import aiohttp
from fastapi.logger import logger
from urllib.parse import ParseResult
from ApiRoute.ApiRouteConfig import config


def make_url(server_name: str, url_path: str):
    for server_info in config.api_server_info:
        if server_info["NM"] == server_name:
            if len(server_info["IP_ADR"]) != 0:
                netloc = server_info["IP_ADR"]
            else:
                netloc = server_info["DOMN_NM"]
            url = ParseResult(
                scheme="http", netloc=netloc, path=url_path, params="", query="", fragment="")
            logger.debug(f"Message Passing Url : {url.geturl()}")
            return url.geturl()
    return None


async def bypass_msg(api_info, params_query, body):
    method = api_info["METH"]
    msg_type = api_info["MSG_TYPE"]

    url = make_url(api_info["CTGRY"], api_info["URL"])
    if url is None:
        return {"result": 0, "errorMessage": "The server info does not exist."}

    async with aiohttp.ClientSession() as session:
        if method == "GET":
            params = {}
            if len(params_query) != 0:
                for param in params_query.split("&"):
                    parser_param = param.split("=")
                    params[parser_param[0]] = parser_param[1]

            async with session.get(url, params=params) as response:
                result = await response.json()
        elif method == "POST":
            if msg_type == "JSON":
                async with session.post(url, json=body) as response:
                    result = await response.json()
            else:
                async with session.post(url, data=body) as response:
                    result = await response.json()
        elif method == "PUT":
            if msg_type == "JSON":
                async with session.put(url, json=body) as response:
                    result = await response.json()
            else:
                async with session.put(url, data=body) as response:
                    result = await response.json()
        else:
            logger.error(f'Method Not Allowed. {method}')
            result = {"result": 0, "errorMessage": "Method Not Allowed."}
    return result


async def run_cmd(cmd):
    async with asyncssh.connect(host=config.remote_info["host"], port=int(config.remote_info["port"]),
                                username=config.remote_info["id"], password=config.remote_info["password"]) as conn:
        result = await conn.run(cmd, check=True)
        logger.debug(f'Command Result : {result.stdout}')
    return result.stdout


async def call_remote_func(api_info, api_params, input_params):
    msg_type = api_info["MSG_TYPE"]

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

    cmd = f'{api_info["CMD"]} {command_input}'

    try:
        result = await run_cmd(cmd)
    except (OSError, asyncssh.Error) as exc:
        logger.error(f'SSH connection failed: {str(exc)}')

    return eval(result)
