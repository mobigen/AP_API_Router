import logging
from typing import Optional, List

from fastapi import Depends, APIRouter
from pydantic import BaseModel
from starlette.responses import JSONResponse

from common_service.app.common.config import settings
from common_service.app.database.conn import db
from libs.database.connector import Executor


class JoinInfo(BaseModel):
    table_nm: str
    key: str


class WhereInfo(BaseModel):
    table_nm: str
    key: str
    value: str
    compare_op: str
    op: Optional[str] = ""
    sub: Optional[List["WhereInfo"]] = None


class OrderInfo(BaseModel):
    table_nm: str
    key: str
    order: str


class PageInfo(BaseModel):
    per_page: int
    cur_page: int


class CommonSelect(BaseModel):
    table_nm: str
    key: Optional[str] = None
    join_info: Optional[JoinInfo] = None
    where_info: Optional[List[WhereInfo]] = None
    order_info: Optional[OrderInfo] = None
    page_info: Optional[PageInfo] = None


router = APIRouter()

logger = logging.getLogger()


@router.post("/common-select")
async def common_select(params: CommonSelect, session: Executor = Depends(db.get_db)):
    try:
        rows = session.query(**params.dict()).all()
        return JSONResponse(
            content={
                "data": {
                    "count": rows[1] if rows else 0,
                    "body": rows[0] if rows else [],
                    "header": session.get_column_info(params.table_nm, settings.DB_INFO.SCHEMA),
                },
                "result": 1,
                "errorMessage": "",
            },
            status_code=200,
        )

    except Exception as e:
        logger.error(f"{params.dict()}, {str(e)}", exc_info=True)
        return JSONResponse(content={"result": 0, "errorMessage": str(e)}, status_code=400)
