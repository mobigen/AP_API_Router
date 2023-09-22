import uvicorn
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI

from batch_service.common.config import settings
from batch_service.database.conn import db
from batch_service.jobs import send_email, recommend_word, els_update
from batch_service.routes import v1


def create_app():
    app_ = FastAPI()
    print(settings.dict())
    db.init_app(app_, **settings.dict())

    app_.include_router(v1.router, prefix="/portal/api/batch")

    return app_


app = create_app()

# 임시 생성 TODO: 객체로 관리 후 주입?
scheduler = BackgroundScheduler()


@app.on_event("startup")
def _app_startup():
    scheduler.add_job(send_email.send_mail, "cron",second="*/5",id="email")
    scheduler.add_job(recommend_word.recommend_search_word, "cron",hour='23', minute='59',id="recommend")
    scheduler.add_job(els_update.insert_meta, "cron", hour='00', minute='15',id="update_meta")
    scheduler.add_job(els_update.insert_ckan, "cron", hour='00', minute='40',id="update_ckan")
    scheduler.start()


@app.on_event("shutdown")
def _app_shutdown():
    scheduler.shutdown()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8090, reload=True)
