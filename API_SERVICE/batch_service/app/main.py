import uvicorn
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI

from batch_service.app.common.config import settings
from batch_service.app.database.conn import seoul_db, db
from batch_service.app.jobs import send_email, recommend_word, els_update, seoul_db_upload
from batch_service.app.routes.v1 import test


def create_app():
    app_ = FastAPI()
    print(settings.dict())
    db.init_app(app_, **settings.dict())

    seoul_db.init_app(app_, DB_INFO=settings.SEOUL_DB_INFO.dict(by_alias=True), **settings.dict(exclude={"DB_INFO"}))

    app_.include_router(test.router, prefix="/portal/api/batch")

    return app_


app = create_app()

# 임시 생성 TODO: 객체로 관리 후 주입?
scheduler = BackgroundScheduler()


@app.on_event("startup")
def _app_startup():
    scheduler.add_job(send_email.send_mail, "cron", second="*/5", id="email")
    scheduler.add_job(recommend_word.recommend_search_word, "cron", hour="23", minute="59", id="recommend")
    scheduler.add_job(els_update.insert_meta, "cron", hour="00", minute="15", id="update_meta")
    scheduler.add_job(els_update.insert_ckan, "cron", hour="00", minute="40", id="update_ckan")
    scheduler.add_job(seoul_db_upload.update_ddr, "cron", hour="23", minute="59", id="update_ddr")
    scheduler.add_job(seoul_db_upload.update_rr, "cron", hour="23", minute="59", id="update_rr")

    scheduler.start()


@app.on_event("shutdown")
def _app_shutdown():
    scheduler.shutdown()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8090, reload=True)