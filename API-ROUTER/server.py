import os
import logging
import logging.config
from Utils.CommonUtil import get_config
from ApiRoute import ApiRoute
from fastapi import FastAPI
import uvicorn
from pathlib import Path


root_path = Path(os.getcwd()).parent
logging.config.fileConfig(os.path.join(root_path, "API-ROUTER/conf/logging.conf"))
logger = logging.getLogger()

if __name__ == '__main__':
    api_router_cfg = get_config(root_path)    
    db_type = api_router_cfg["default"]["db"]
    db_info = api_router_cfg[db_type]
    
    host = api_router_cfg["default"]["host"]
    port = api_router_cfg["default"]["port"]
    
    api_router = ApiRoute(db_type, db_info)
    app = FastAPI()
    app.include_router(api_router.router)
    #uvicorn.run("server:app", host=host, port=int(port))#, reload=True)
    uvicorn.run(app, host=host, port=int(port))#, reload=True)
