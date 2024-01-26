import logging

import uvicorn
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

from common_service.app.common.config import settings
from common_service.app.database.conn import db
from common_service.app.routes.v1 import code_info, select, execute, auth_email
from libs.auth.keycloak import keycloak
from libs.middlewares.keycloak_middleware import refresh_token_from_cookie_wrapper

logger = logging.getLogger()


def create_app():
    app_ = FastAPI()
    logger.info(settings.dict())
    db.init_app(app_, **settings.dict())

    keycloak.set_url(settings.KEYCLOAK_INFO.KEYCLOAK_URL)
    app_.add_middleware(
        BaseHTTPMiddleware,
        dispatch=refresh_token_from_cookie_wrapper(
            keycloak=keycloak,
            realm=settings.KEYCLOAK_INFO.REALM,
            client_id=settings.KEYCLOAK_INFO.CLIENT_ID,
            client_secret=settings.KEYCLOAK_INFO.CLIENT_SECRET,
            logger=logger,
        ),
    )

    app_.include_router(select.router, prefix="/portal/api/common")
    app_.include_router(execute.router, prefix="/portal/api/common")
    app_.include_router(auth_email.router, prefix="/portal/api/common")
    app_.include_router(code_info.router, prefix="/portal/api/sitemng")

    return app_


app = create_app()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8090, reload=True)
