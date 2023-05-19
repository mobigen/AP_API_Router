from typing import Dict, List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from common_service.database.conn import db
from libs.database.connector import Connector


class CommonExecute(BaseModel):
    method: str
    table_nm: str
    data: Dict
    key: Optional[List[str]] = None


router = APIRouter()


@router.post("/common-execute")
async def common_execute(params: List[CommonExecute], session: Connector = Depends(db.get_db)):
    for param in params:
        session.execute(**param.dict())
    return {"result": 1, "errorMessage": ""}
