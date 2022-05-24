import requests
from fastapi.logger import logger
from ApiRoute.ApiRouteConfig import config
from ConnectManager import RemoteCmd


def make_url(server_name: str, url: str):
    for server_info in config.api_server_info:
        if server_info["name"] == server_name:
            if len(server_info["ip_port"]) != 0:
                return f'http://{server_info["ip_port"]}{url}'
            else:
                return f'http://{server_info["domain"]}{url}'
    return None


def bypass_msg(api_info, params_query, body):
    method = api_info["method"]
    msg_type = api_info["msg_type"]

    url = make_url(api_info["category"], api_info["url"])
    if url is None:
        return {"result": 0, "errorMessage": "The server info does not exist."}

    if method == "GET":
        params = {}
        if len(params_query) != 0:
            for param in params_query.split("&"):
                parser_param = param.split("=")
                params[parser_param[0]] = parser_param[1]
        response = requests.get(url, params=params)
    elif method == "POST":
        if msg_type == "JSON":
            response = requests.post(url, json=body)
        else:
            response = requests.post(url, data=body)
    elif method == "PUT":
        if msg_type == "JSON":
            response = requests.put(url, json=body)
        else:
            response = requests.put(url, data=body)
    else:
        logger.error(f'Method Not Allowed. {method}')
        return {"result": 0, "errorMessage": "Method Not Allowed."}
    return response.json()


def call_remote_func(api_info, api_params, input_params):
    msg_type = api_info["msg_type"]

    remote_cmd = RemoteCmd(
        config.remote_info["host"], config.remote_info["port"], config.remote_info["id"], config.remote_info["password"])
    command_input = ""
    if msg_type == "JSON":
        for param in api_params:
            try:
                data = input_params[param["param_name"]]
                command_input += f' --{param["param_name"]} {data}'
            except KeyError:
                print(
                    f'parameter set default value. [{param["param_name"]}]')
                command_input += f' --{param["param_name"]} {param["default_value"]}'

    cmd = f'{api_info["command"]} {command_input}'
    result = eval(remote_cmd.cmd_exec(cmd))
    return result
