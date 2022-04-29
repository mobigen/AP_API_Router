import os
import logging
import logging.config
import traceback
from fastapi import FastAPI
import uvicorn
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import prepare_config
from ApiService import ApiService
import pdb

prepare_config()
#logging.config.fileConfig(os.path.join(config.root_path, "AP_API_Router/API-ROUTER/conf/logging.conf"))
#logger = logging.getLogger()
api_router = ApiService()
app = FastAPI()
app.include_router(api_router.router)
if __name__ == '__main__':
    uvicorn.run("server:app", host=config.server_host, port=config.server_port, reload=True)
