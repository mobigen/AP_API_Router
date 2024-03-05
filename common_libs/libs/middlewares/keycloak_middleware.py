from ast import literal_eval
import logging
from fastapi import HTTPException, Request
from datetime import datetime

from libs.auth.keycloak import KeycloakManager

REFRESH_SEC = 60 * 50


def get_token_from_cookie(cookies):
    for k, v in cookies.items():
        if "token" in k:
            return k, v


def refresh_token_from_cookie_wrapper(keycloak: KeycloakManager, **kwargs):
    logger: logging.Logger = kwargs.get("logger")

    async def refresh_with_cookie(request: Request, call_next):
        dat = get_token_from_cookie(request.cookies)
        if not dat:
            logger.debug(f"token none :: {request.cookies}")
            return await call_next(request)

        logger.info(dat)
        cookie_name = dat[0]
        try:
            token = literal_eval(dat[1])
            if token.get("status_code") >= 400:
                raise HTTPException(status_code=token.get("status_code"))
        except Exception as e:
            response = await call_next(request)
            response.delete_cookie(cookie_name, domain=kwargs.get("domain"))
            return response

        now = datetime.now().strftime("%s")
        diffTime = REFRESH_SEC + 1
        try:
            createTime = token.get("create_time")
            diffTime = float(now) - float(createTime)
        except Exception:
            pass

        logger.info(f"createTime :: {createTime}")
        logger.info(f"diffTime :: {diffTime}")

        if diffTime > REFRESH_SEC:
            logger.info("Refresh Token!!")
            res = await keycloak.refresh_token(
                realm=kwargs.get("realm"),
                client_id=kwargs.get("client_id"),
                client_secret=kwargs.get("client_secret"),
                grant_type="refresh_token",
                refresh_token=token["data"]["refresh_token"],
            )
            res["create_time"] = datetime.now().strftime("%s")
        else:
            logger.info("Token Maintain!!")
            res = token

        api_response = await call_next(request)
        api_response.set_cookie(key=cookie_name, value=res, domain=kwargs.get("domain"))
        return api_response

    return refresh_with_cookie
