import os
import logging
import logging.config
from Utils.CommonUtil import get_config
from fastapi import FastAPI
import uvicorn
from ApiService import ApiService
from pathlib import Path
import uvicorn

root_path = Path(os.getcwd()).parent
logging.config.fileConfig(os.path.join(root_path, "AP_API_Router/API-SERVICE/conf/logging.conf"))
logger = logging.getLogger()
api_service_cfg = get_config(root_path)    

db_type = api_service_cfg["default"]["db"]
db_info = api_service_cfg[db_type]
qury_info = api_service_cfg["select_query"]

app = FastAPI()
api_service = ApiService(db_type, db_info, qury_info)
app.include_router(api_service.router)

if __name__ == '__main__':    
    host = api_service_cfg["default"]["host"]
    port = api_service_cfg["default"]["port"]

    uvicorn.run("server:app", host=host, port=int(port), reload=True)
