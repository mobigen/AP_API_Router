from typing import Dict
from fastapi.logger import logger
from ServiceUtils import CommonUtil as utils
from starlette.requests import Request


def api(request: Request) -> Dict:
    try:
        token = utils.get_token_from_cookie(request)
        payload = utils.jwt_decode(token)
        user = utils.get_user_info(payload)
        logger.info(f"CommonUserInfo :: {user}")
    except Exception:
        except_name = utils.get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = {"result": 1, "errorMessage": "", "data": {"body": payload}}

    return result
