from common_service.routes.v1 import select
import uvicorn
from fastapi import FastAPI

from common_service.common.config import settings
from common_service.database.conn import db


def create_app():
    app_ = FastAPI()
    print(settings.dict())
    db.init_app(app_, **settings.dict())

    app_.include_router(select.router, prefix="/portal/api/common")

    return app_


app = create_app()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8090, reload=True)
