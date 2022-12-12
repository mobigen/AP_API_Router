from datetime import timedelta
from typing import Dict

from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import (
    get_exception_info,
    create_token,
    make_token_data,
    authenticate_user,
)


class commonLogin(BaseModel):
    data: Dict


def api(login: commonLogin):
    """
    id_column = user_id
    password_column = user_password
    """
    access_token = ""
    try:
        user = authenticate_user(
            login.data[config.user_info["id_column"]],
            login.data[config.user_info["password_column"]],
        )
        token_data = make_token_data(user)
        access_token = create_token(
            data=token_data,
            expires_delta=timedelta(minutes=int(config.secret_info["expire_min"])),
        )
        result = {"result": 1, "errorMessage": ""}
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}

    response = JSONResponse(content=result)
    response.set_cookie(key=config.secret_info["cookie_name"], value=access_token)
    return response
