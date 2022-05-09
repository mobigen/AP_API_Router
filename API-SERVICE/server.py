from fastapi import FastAPI
import uvicorn
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import prepare_config
from ApiService import ApiService

prepare_config()
api_router = ApiService()
app = FastAPI()
app.include_router(api_router.router)

if __name__ == '__main__':
    uvicorn.run("server:app", host=config.server_host, port=config.server_port,
                reload=True, log_config=f'{config.root_path}/API-SERVICE/conf/logging.conf')
