from ast import literal_eval
import logging
from fastapi import HTTPException, Request

from libs.auth.keycloak import KeycloakManager


def get_token_from_cookie(cookies):
    for k, v in cookies.items():
        if "token" in k:
            return k, v


def refresh_token_from_cookie_wrapper(keycloak: KeycloakManager, **kwargs):
    logger: logging.Logger = kwargs.get("logger")

    async def refresh_with_cookie(request: Request, call_next):
        dat = get_token_from_cookie(request.cookies)
        if not dat:
            return await call_next(request)

        logger.info(dat)
        cookie_name = dat[0]
        try:
            token = literal_eval(dat[1])
            if token.get("status_code") >= 400:
                raise HTTPException(status_code=token.get("status_code"))
        except Exception as e:
            response = await call_next(request)
            response.delete_cookie(cookie_name)
            return response

        res = await keycloak.refresh_token(
            realm=kwargs.get("realm"),
            client_id=kwargs.get("client_id"),
            client_secret=kwargs.get("client_secret"),
            grant_type="refresh_token",
            refresh_token=token["data"]["refresh_token"],
        )

        api_response = await call_next(request)
        api_response.set_cookie(key=cookie_name, value=res)
        return api_response

    return refresh_with_cookie
