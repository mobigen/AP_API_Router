import uvicorn
from fastapi import FastAPI
from login_service.routes.v1.login import login
from login_service.common.config import settings
from login_service.database.conn import db


def create_app():
    app_ = FastAPI()
    print(settings.dict())
    db.init_app(app_, **settings.dict())

    app_.include_router(login.router, prefix="/portal/api/common")

    return app_


app = create_app()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8090, reload=True)
