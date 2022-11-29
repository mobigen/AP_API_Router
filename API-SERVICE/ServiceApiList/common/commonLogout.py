from typing import Dict
from fastapi.logger import logger
from fastapi.responses import JSONResponse
from jose import jwt
from starlette.requests import Request

from ServiceUtils import CommonUtil as utils
from ApiService.ApiServiceConfig import config


def api(request: Request) -> Dict:
    f_delete = True
    try:
        token = utils.get_token_from_cookie(request)
        payload = utils.jwt_decode(token)
        user = utils.get_user_info(payload)
    except Exception:
        except_name = utils.get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
        # f_delete = False  # 쿠기를 삭제하지 않으면 user-docean-access-token에 None 값이 들어가고 이는 Exception 발생을 야기
    else:
        result = {"result": 1, "errorMessage": ""}
    response = JSONResponse(content=result)
    if f_delete:
        response.delete_cookie(key=config.secret_info["cookie_name"])
        response.delete_cookie(key=config.secret_info["knime_cookie_name"])
    return response
