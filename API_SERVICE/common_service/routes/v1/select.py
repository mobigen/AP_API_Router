import logging
from typing import Optional, List

from fastapi import Depends, APIRouter
from pydantic import BaseModel

from common_service.database.conn import db
from libs.database.connector import Connector


class JoinInfo(BaseModel):
    table_nm: str
    key: str


class WhereInfo(BaseModel):
    table_nm: str
    key: str
    value: str
    compare_op: str
    op: Optional[str] = ""
    sub_conditions: Optional[List["WhereInfo"]] = None


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


@router.post("/common-select", response_model=dict)
async def common_select(params: CommonSelect, session: Connector = Depends(db.get_db)):
    """
    {
        "table_nm":"banr_adm_bas",
        "where_info":[
            {
                "key":"banr_div",
                "value":"T",
                "table_nm":"banr_adm_bas",
                "compare_op":"Equal","op":""
            },
            {
                "key":"pstng_fns_date",
                "compare_op":">=",
                "value":"2023-04-12 00:00:00",
                "table_nm":"banr_adm_bas",
                "op":"AND"
            }
        ]
    }
    {"table_nm":"vw_srhwd_find_tmscnt_sum","order_info":{"key":"find_tmscnt","value":"DESC","table_nm":"vw_srhwd_find_tmscnt_sum","order":"DESC"},"page_info":{"per_page":10,"cur_page":1}}
    """
    try:
        logger.info(params.dict())
        rows = session.query(**params.dict()).all()
        result = {
            "data": {
                "count": rows[1] if rows else 0,
                "body": rows[0] if rows else [],
                "header": session.get_column_info(params.table_nm),
            },
            "result": 1,
            "errorMessage": "",
        }

    except Exception as e:
        result = {"result": 0, "errorMessage": str(e)}
        logger.error(e, exc_info=True)
    return result
