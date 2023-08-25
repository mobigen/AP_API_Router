from fastapi import Request
from libs.auth.keycloak import keycloak

from libs.exceptions import TokenDoesNotExist
from login_service.common.config import settings


def get_token_from_cookie(cookies):
    for k, v in cookies.items():
        if "token" in k:
            return k, v


async def refresh_with_cookie(request: Request, call_next):
    dat = get_token_from_cookie(request.cookies)
    if not dat or not dat[1]:
        return await call_next(request)

    cookie_name = dat[0]
    token = dat[1]

    res = await keycloak.refresh_token(
        realm=settings.KEYCLOAK_INFO.realm,
        client_id=settings.KEYCLOAK_INFO.client_id,
        client_secret=settings.KEYCLOAK_INFO.client_secret,
        grant_type="refresh_token",
        refresh_token=token["data"]["refresh_token"],
    )

    api_response = await call_next(request)
    api_response.set_cookie(key=cookie_name, value=res)
    return api_response
