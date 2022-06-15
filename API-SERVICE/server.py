from fastapi import FastAPI
import uvicorn
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import prepare_config
from ApiService import ApiService
import os

prepare_config()
api_router = ApiService()
app = FastAPI()
app.include_router(api_router.router)

if __name__ == '__main__':
    log_dir = f'{config.root_path}/API-SERVICE/log/{config.category}'
    if os.path.isdir(log_dir):
        print(f"Directory Exists")
    else:
        print(f"Make log dir : {log_dir}")
        os.makedirs(log_dir)
    uvicorn.run("server:app", host=config.server_host, port=config.server_port,
                reload=True, log_config=f'{config.root_path}/API-SERVICE/conf/{config.category}/logging.conf')
