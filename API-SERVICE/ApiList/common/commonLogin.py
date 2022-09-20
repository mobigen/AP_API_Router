from http import cookies
from http.cookiejar import Cookie
from typing import Dict
from pydantic import BaseModel
from fastapi.logger import logger
from fastapi.responses import JSONResponse
from datetime import timedelta
from Utils.CommonUtil import get_exception_info, create_token, make_token_data, authenticate_user
from ApiService.ApiServiceConfig import config


class commonLogin(BaseModel):
    data: Dict


def api(login: commonLogin) -> Dict:
    access_token = ""
    try:
        user = authenticate_user(
            login.data[config.user_info["id_column"]], login.data[config.user_info["password_column"]])
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:

        token_data = make_token_data(user)
        access_token = create_token(
            data=token_data, expires_delta=timedelta(minutes=int(config.secret_info["expire_min"])))
        result = {"result": 1, "errorMessage": ""}

    response = JSONResponse(content=result)
    response.set_cookie(
        key=config.secret_info["cookie_name"], value=access_token)
    return response
