import importlib.util
from fastapi.logger import logger
from fastapi import APIRouter
from ApiService.ApiServiceConfig import config


class ApiService:
    def __init__(self) -> None:
        self.router = APIRouter()
        self.set_route()

    def set_route(self) -> None:
        for api_name, api_info in config.api_config.items():
            if config.category == api_info["sub_dir"]:
                module_name = f'ServiceApiList.{api_info["sub_dir"]}.{api_name}'
                spec = importlib.util.find_spec(module_name)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self.router.add_api_route(f'{api_info["url"]}',
                                          module.api, methods=[
                                              api_info["method"]],
                                          tags=[f'service [ {api_info["sub_dir"]} ]'])
