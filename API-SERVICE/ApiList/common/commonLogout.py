from typing import Dict
from fastapi.logger import logger
#from fastapi.responses import JSONResponse
from jose import jwt
from starlette.requests import Request
from Utils.CommonUtil import get_exception_info, get_user
from ApiService.ApiServiceConfig import config


class InvalidUserInfo(Exception):
    pass


class TokenDoesNotExist(Exception):
    pass


def api(request: Request) -> Dict:
    #f_delete = True
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
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
        #f_delete = False
    else:
        result = {"result": 1, "errorMessage": ""}
    #response = JSONResponse(content=result)
    # if f_delete:
    #    response.delete_cookie(key=config.secret_info["cookie_name"])
    # return response
    return result
