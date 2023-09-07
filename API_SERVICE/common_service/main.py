from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn
from fastapi import FastAPI

from common_service.common.config import settings
from common_service.database.conn import db
from common_service.routes.v1 import select, execute, auth_email
import logging
from libs.auth.keycloak import keycloak

from libs.middlewares.keycloak_middleware import refresh_token_from_cookie_wrapper

logger = logging.getLogger()


def create_app():
    app_ = FastAPI()
    logger.info(settings.dict())
    db.init_app(app_, **settings.dict())

    keycloak.set_url("https://auth.bigdata-car.kr")
    app_.add_middleware(
        BaseHTTPMiddleware,
        dispatch=refresh_token_from_cookie_wrapper(
            keycloak=keycloak,
            realm="mobigen",
            client_id="katech",
            client_secret="ZWY7WDimS4rxzaXEfwEShYMMly00i8L0",
            logger=logger,
        ),
    )

    app_.include_router(select.router, prefix="/portal/api/common")
    app_.include_router(execute.router, prefix="/portal/api/common")
    app_.include_router(auth_email.router, prefix="/portal/api/common")

    return app_


app = create_app()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8090, reload=True)
