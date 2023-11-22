import logging

import uvicorn
from fastapi import FastAPI

from libs.auth.keycloak import keycloak
from libs.disk.mydisk import mydisk
from mydisk_service.app.common.config import settings
from mydisk_service.app.database.conn import db
from mydisk_service.app.routes.v1 import disk, s3

logger = logging.getLogger()


def create_app():
    app_ = FastAPI()
    print(settings.dict())
    db.init_app(app_, **settings.dict())
    keycloak.set_url(settings.KEYCLOAK_INFO.keycloak_url)
    mydisk.set_url(settings.MYDISK_INFO.mydisk_url)

    app_.include_router(disk.router, prefix="/portal/api/mydisk")
    app_.include_router(s3.router, prefix="/portal/api/s3")

    return app_


app = create_app()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8090, reload=True)
