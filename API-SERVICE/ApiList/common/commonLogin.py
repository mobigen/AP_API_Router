from datetime import timedelta
from typing import Dict
from fastapi.logger import logger

from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import (
    get_exception_info,
    create_token,
    get_keycloak_manager,
    make_token_data,
    authenticate_user,
)


class commonLogin(BaseModel):
    data: Dict


async def api(login: commonLogin):
    """
    id_column = user_id
    password_column = user_password
    """
    dat = {}
    try:
        user_id = login.data.get(config.user_info["id_column"], None)
        if not user_id:
            dat["grant_type"] = "refresh_token"
            dat["refresh_token"] = login.data.get("refresh_token")
        else:
            dat["username"] = user_id
            dat["grant_type"] = "password"
            user_pwd = login.data[config.user_info["password_column"]]
            authenticate_user(user_id, user_pwd)
            dat["password"] = user_pwd

        token = await get_token(**dat)

        response = JSONResponse(content={"result": 1, "errorMessage": ""})
        response.set_cookie(key=config.secret_info["cookie_name"], value=token)
        return response
    except Exception as e:
        except_name = get_exception_info()
        logger.error(e, exc_info=True)
        return JSONResponse(content={"result": 0, "errorMessage": except_name})


async def get_token(grant_type, refresh_token="", username="", password=""):
    client_id = config.keycloak_info["client_id"]
    client_secret = config.keycloak_info["client_secret"]
    realm = config.keycloak_info["realm"]
    return await get_keycloak_manager().generate_normal_token(
        realm=realm,
        client_id=client_id,
        client_secret=client_secret,
        grant_type=grant_type,
        refresh_token=refresh_token,
        username=username,
        password=password,
    )
