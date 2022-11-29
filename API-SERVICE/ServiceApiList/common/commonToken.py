from typing import Dict
from fastapi.logger import logger
from fastapi.responses import JSONResponse
from datetime import timedelta
from jose import jwt
from ServiceUtils import CommonUtil as utils
from ServiceUtils.exceptions import TokenDoesNotExist, InvalidUserInfo
from ApiService.ApiServiceConfig import config
from starlette.requests import Request





def api(request: Request) -> Dict:
    access_token = ""
    try:
        token = utils.get_token_from_cookie(request)
        payload = utils.jwt_decode(token)
        user = utils.get_user_info(payload)
    except Exception:
        except_name = utils.get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        token_data = utils.make_token_data(user)
        access_token = utils.create_token(
            data=token_data,
            expires_delta=timedelta(minutes=int(config.secret_info["expire_min"])),
            secret_key=config.secret_info["secret_key"],
            algorithm=config.secret_info["algorithm"],
        )
        result = {"result": 1, "errorMessage": ""}

    response = JSONResponse(content=result)
    response.set_cookie(
        key=config.secret_info["cookie_name"], value=access_token, max_age=3600, secure=False, httponly=True
    )
    return response
