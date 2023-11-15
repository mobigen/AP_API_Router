import logging

import uvicorn
from fastapi import FastAPI

from meta_service.app.common.config import settings
from meta_service.app.database.conn import db
from meta_service.app.routes.v1 import els, category, meta_insert
logger = logging.getLogger()


def create_app():
    app_ = FastAPI()
    logger.info(settings.dict())
    db.init_app(app_, **settings.dict())

    app_.include_router(category.router, prefix="/portal/api/meta")
    app_.include_router(els.router, prefix="/portal/api/meta")
    app_.include_router(meta_insert.router, prefix="/portal/api/meta")
    return app_


app = create_app()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8090, reload=True)
