import uvicorn
from fastapi import FastAPI
from libs.auth.keycloak import keycloak
from login_service.routes.v1 import auth as authV1
from login_service.routes.v2 import auth as authV2
from login_service.routes.v2 import iris_sso
from login_service.common.config import settings
from login_service.database.conn import db

import logging

logger = logging.getLogger()


def create_app():
    app_ = FastAPI()
    print(settings.dict())
    db.init_app(app_, **settings.dict())
    keycloak.set_url(settings.KEYCLOAK_INFO.keycloak_url)

    app_.include_router(authV1.router, prefix="/portal/api/common")
    app_.include_router(authV2.router, prefix="/portal/api/common")
    app_.include_router(iris_sso.router, prefix="/portal/api/common")

    return app_


app = create_app()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8090, reload=True)
