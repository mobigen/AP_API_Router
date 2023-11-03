import logging

import uvicorn
from fastapi import FastAPI

from common_service.app.common.config import settings
from common_service.app.database.conn import db
from common_service.app.routes.v1 import select, execute


logger = logging.getLogger()


def create_app():
    app_ = FastAPI()
    logger.info(settings.dict())
    db.init_app(app_, **settings.dict())

    app_.include_router(select.router, prefix="/portal/api/common")
    app_.include_router(execute.router, prefix="/portal/api/common")

    return app_


app = create_app()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8090, reload=True)
