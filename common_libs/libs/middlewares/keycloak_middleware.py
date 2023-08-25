from ast import literal_eval
import logging
from fastapi import Request
from libs.auth.keycloak import keycloak


def get_token_from_cookie(cookies):
    for k, v in cookies.items():
        if "token" in k:
            return k, v


def refresh_token_from_cookie_wrapper(realm, client_id, client_secret):
    async def refresh_with_cookie(request: Request, call_next):
        dat = get_token_from_cookie(request.cookies)
        if not dat or not dat[1]:
            return await call_next(request)

        cookie_name = dat[0]
        token = literal_eval(dat[1])

        res = await keycloak.refresh_token(
            realm=realm,
            client_id=client_id,
            client_secret=client_secret,
            grant_type="refresh_token",
            refresh_token=token["data"]["refresh_token"],
        )

        api_response = await call_next(request)
        api_response.set_cookie(key=cookie_name, value=res)
        return api_response

    return refresh_with_cookie
