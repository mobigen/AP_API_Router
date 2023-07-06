import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from starlette.responses import JSONResponse

from common_service.common.const import NOT_ALLOWED_TABLES
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
async def common_execute(request: Request, params: List[CommonExecute], session: Executor = Depends(db.get_db)):
    try:
        for param in params:
            if param.table_nm in NOT_ALLOWED_TABLES:
                ...
                # TODO: 유저 테이블등 수정,삭제 제한이 있는 테이블에 관한 필터링 필요

            session.execute(**param.dict())
        return JSONResponse(content={"result": 1, "errorMessage": ""}, status_code=200)
    except Exception as e:
        logger.error(f"{str(e)}", exc_info=True)
        for param in params:
            logger.info(param.dict())
        return JSONResponse(content={"result": 0, "errorMessage": str(e)}, status_code=400)
