import logging

import uvicorn
from fastapi import FastAPI

from router.app.common.config import settings
from router.app.database.conn import db
from router.app.routes import index

logger = logging.getLogger()


def create_app():
    """
    1. prepare_config
    2. include_router
    """

    app_ = FastAPI()
    # db init
    logger.info(settings.dict())
    db.init_app(app_, **settings.dict())
    # middleware init
    # router init
    app_.include_router(index.router, tags=["index"])

    return app_


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=9010,
        reload=True,
    )
