from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_token_info, make_res_msg
from fastapi.logger import logger
from starlette.requests import Request


def api(request: Request) -> Dict:
    logger.error(request.json())
    result = {"result": 0, "errorMessage": "postTest"}

    return result
