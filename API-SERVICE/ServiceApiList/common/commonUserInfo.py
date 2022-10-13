from typing import Dict
from fastapi.logger import logger
from jose import jwt
from ServiceUtils.CommonUtil import get_exception_info, get_user
from ApiService.ApiServiceConfig import config
from starlette.requests import Request


class InvalidUserInfo(Exception):
    pass


class TokenDoesNotExist(Exception):
    pass


def api(request: Request) -> Dict:
    try:
        recv_access_token = request.cookies.get(
            config.secret_info["cookie_name"])
        if not recv_access_token:
            raise TokenDoesNotExist
        payload = jwt.decode(token=recv_access_token,
                             key=config.secret_info["secret_key"], algorithms=config.secret_info["algorithm"])
        username = payload[config.user_info["id_column"]]
        user = get_user(username)
        if not user[0]:
            raise InvalidUserInfo
        user = user[0][0]
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = {"result": 1, "errorMessage": "", "data": {"body": payload}}

    return result
