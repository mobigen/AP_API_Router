import logging

import uvicorn
from fastapi import FastAPI

from libs.els.ELKSearch.Utils.base import set_els
from libs.els.ELKSearch.index import Index

from meta_service.app.common.config import settings, base_dir
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


# @app.on_event("startup")
# def _init_elasticsearch():
#     es = set_els(host=settings.ELS_INFO.ELS_HOST, port=settings.ELS_INFO.ELS_PORT)
#     logger.info(Index(es).init_els_all_index(f"{base_dir}/resources/ELK/elasticsearch/mapping"))
#
#     with db.get_db_manager() as session:
#         logger.info(els.meta_update_bulk(session))
#         logger.info(els.oversea_update_bulk(session))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8090, reload=True)
