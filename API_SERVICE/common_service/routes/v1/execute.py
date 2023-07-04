import logging
from typing import Dict, List, Optional

import jwt
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from starlette.responses import JSONResponse

from common_service.common.const import ALGORITHM, NOT_ALLOWED_TABLES, SECRET_KEY
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
            table_nm = param.table_nm
            method = param.method
            if table_nm in NOT_ALLOWED_TABLES:
                roleidx = get_roleidx_from_token(request)
                if roleidx != "0":
                    return JSONResponse(content={"result": 0, "errorMessage": "NotAllowedTable"})
                elif table_nm == "USR_MGMT" and method == "INSERT":
                    return JSONResponse(content={"result": 0, "errorMessage": "use register api"})
            session.execute(**param.dict())
        return JSONResponse(content={"result": 1, "errorMessage": ""}, status_code=200)
    except Exception as e:
        logger.error(f"{str(e)}", exc_info=True)
        for param in params:
            logger.info(param.dict())
        return JSONResponse(content={"result": 0, "errorMessage": str(e)}, status_code=400)


def get_roleidx_from_token(request: Request) -> dict:
    token = request.headers.get("Authorization")
    if token.startswith("Bearer "):
        token = token[7:]
    return dict(jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)).get("roleidx")
