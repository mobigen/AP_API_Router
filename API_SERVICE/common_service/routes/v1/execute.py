import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from starlette.responses import JSONResponse

from common_service.database.conn import db
from libs.database.connector import Executor

logger = logging.getLogger()


class CommonExecute(BaseModel):
    method: str
    table_nm: str
    data: Dict
    key: Optional[List[str]] = None


router = APIRouter()


@router.post("/common-execute")
async def common_execute(params: List[CommonExecute], session: Executor = Depends(db.get_db)):
    try:
        for param in params:
            session.execute(**param.dict())
        return JSONResponse(content={"result": 1, "errorMessage": ""}, status_code=200)
    except Exception as e:
        logger.error(f"{params}, {str(e)}", exc_info=True)
        return JSONResponse(content={"result": 0, "errorMessage": str(e)}, status_code=400)
