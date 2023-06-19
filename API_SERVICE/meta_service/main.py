import uvicorn
from fastapi import FastAPI

from meta_service.common.config import logger
from meta_service.common.config import settings
from meta_service.database.conn import db
from meta_service.routes.v2 import autocomplete, els_data_search, els_bulk_update, els_upsert


def create_app():
    app_ = FastAPI()
    logger.info(settings.dict())
    db.init_app(app_, **settings.dict())

    app_.include_router(autocomplete.router, prefix="/portal/api/meta")
    app_.include_router(els_data_search.router, prefix="/portal/api/meta")
    app_.include_router(els_bulk_update.router, prefix="/portal/api/meta")
    app_.include_router(els_upsert.router, prefix="/portal/api/meta")

    return app_


app = create_app()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8090, reload=True)
