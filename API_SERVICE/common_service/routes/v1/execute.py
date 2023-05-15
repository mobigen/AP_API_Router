from typing import Dict, List, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from common_service.database.conn import db
from starlette.responses import JSONResponse


class CommonExecute(BaseModel):
    method: str
    table_nm: str
    data: Dict
    key: Optional[List[str]] = None


router = APIRouter()


@router.post("/common-execute")
async def common_execute(params: List[CommonExecute], session: Session = Depends(db.get_db)):
    for param in params:
        session.execute(**param.dict())
    return {"result": 1, "errorMessage": ""}
