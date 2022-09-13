from typing import Dict
from fastapi.logger import logger
from fastapi.responses import JSONResponse
from datetime import timedelta
from jose import jwt
from Utils.CommonUtil import get_exception_info, get_user, create_token, make_token_data
from ApiService.ApiServiceConfig import config
from starlette.requests import Request


class InvalidUserInfo(Exception):
    pass


class TokenDoesNotExist(Exception):
    pass


def api(request: Request) -> Dict:
    try:
        access_token = request.headers.get(config.secret_info["header_name"])
        if not access_token:
            raise TokenDoesNotExist
        payload = jwt.decode(token=access_token,
                             key=config.secret_info["secret_key"], algorithms=config.secret_info["algorithm"])
        username = payload[config.user_info["id_column"]]
        user = get_user(username)
        if not user[0]:
            raise InvalidUserInfo
        user = user[0][0]
    except Exception:
        except_name = get_exception_info()
        access_token = ""
        result = {"result": 0, "errorMessage": except_name}
    else:
        token_data = make_token_data(user)
        access_token = create_token(data=token_data, expires_delta=timedelta(
            minutes=int(config.secret_info["expire_min"])))
        result = {"result": 1, "errorMessage": ""}

    return JSONResponse(content=result, headers={config.secret_info["header_name"]: access_token})
