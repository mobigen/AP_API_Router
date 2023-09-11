import os

import uvicorn
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI

from ApiService import ApiService
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import prepare_config, set_log_path


prepare_config()
api_router = ApiService()
app = FastAPI()
app.include_router(api_router.router)


@app.on_event("startup")
async def startup():
    if config.category == "common":
        from Utils import batch_email
        scheduler = BackgroundScheduler()
        scheduler.add_job(batch_email.email_handler, "interval", seconds=5, id="sender")
        scheduler.start()


if __name__ == "__main__":
    log_dir = f"{config.root_path}/log/{config.category}"
    if os.path.isdir(log_dir):
        print("Directory Exists")
    else:
        print(f"Make log dir : {log_dir}")
        os.makedirs(log_dir)

    set_log_path()
    uvicorn.run(
        "server:app",
        host=config.server_host,
        port=config.server_port,
        reload=True,
        log_config=f"{config.root_path}/conf/{config.category}/logging.conf",
    )
