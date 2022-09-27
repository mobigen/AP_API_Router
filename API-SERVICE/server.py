from fastapi import FastAPI
import uvicorn
from pathlib import Path
from ApiService.ApiServiceConfig import config
from ServiceUtils.CommonUtil import prepare_config, set_log_path
from ApiService import ApiService
import os

root_path = str(Path(os.path.dirname(os.path.abspath(__file__))))
prepare_config(root_path)
api_router = ApiService()
app = FastAPI()
app.include_router(api_router.router)

if __name__ == '__main__':
    log_dir = f'{config.root_path}/log/{config.category}'
    if os.path.isdir(log_dir):
        print(f"Directory Exists")
    else:
        print(f"Make log dir : {log_dir}")
        os.makedirs(log_dir)

    set_log_path()
    uvicorn.run("server:app", host=config.server_host, port=config.server_port,
                reload=True, log_config=f'{config.root_path}/conf/{config.category}/logging.conf')
