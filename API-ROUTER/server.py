from fastapi import FastAPI
import uvicorn
from ApiRoute.ApiRouteConfig import config
from Utils.CommonUtil import prepare_config, set_log_path
from ApiRoute import ApiRoute
import os

prepare_config()
api_router = ApiRoute()
app = FastAPI()
app.include_router(api_router.router)

if __name__ == "__main__":
    log_dir = f"{config.root_path}/log"
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
        log_config=f"{config.root_path}/conf/logging.conf",
    )
