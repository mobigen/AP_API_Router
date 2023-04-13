from typing import Optional, List, Union

import sqlalchemy
from fastapi import Depends, APIRouter
from pydantic import BaseModel
from sqlalchemy import Column, or_, and_, not_
from sqlalchemy.orm import Session

from common_service.database.conn import db


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


@router.post("/common-select", response_model=dict)
async def read_data(common_select: CommonSelect, session: Session = Depends(db.get_db)):
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
    Args:
        common_select (CommonSelect): _description_
        session (Session, optional): _description_. Defaults to Depends(db.get_db).
        table_dict (dict, optional): _description_. Defaults to Depends(db.get_meta_tables).

    Raises:
        e: _description_

    Returns:
        _type_: _description_
    """
    query = None
    base_table = db.get_table(common_select.table_nm)
    key = common_select.key
    try:
        # Join
        if join_info := common_select.join_info:
            join_table = db.get_table(join_info.table_nm)
            query = session.query(base_table, join_table).join(
                join_table,
                getattr(base_table.columns, key) == getattr(join_table.columns, join_info.key),
            )
        else:
            query = session.query(base_table)

        # Where
        if where_info := common_select.where_info:
            filter_val = None
            for where_condition in where_info:
                filter_condition = str_to_filter(
                    getattr(base_table.columns, where_condition.key),
                    where_condition.value,
                    where_condition.compare_op,
                )
                if sub_conditions := where_condition.sub_conditions:
                    for sub_condition in sub_conditions:
                        sub_filter_condition = str_to_filter(
                            getattr(base_table.columns, sub_condition.key),
                            sub_condition.value,
                            sub_condition.compare_op,
                        )
                        # or_ , | 사용무관
                        if sub_condition.op.lower() == "or":
                            filter_condition = or_(filter_condition, sub_filter_condition)
                        elif sub_condition.op.lower() == "and":
                            filter_condition = and_(filter_condition, sub_filter_condition)

                if filter_val is not None:
                    if where_condition.op.lower() == "or":
                        filter_val = filter_val | filter_condition
                    elif where_condition.op.lower() == "and":
                        filter_val = filter_val & filter_condition
                else:
                    filter_val = filter_condition
            query = query.filter(filter_val)

        count = query.count()

        # Order
        if order_info := common_select.order_info:
            order_key = getattr(base_table.columns, order_info.key)
            query = query.order_by(getattr(sqlalchemy, order_info.order.lower())(order_key))

        # Paging
        if page_info := common_select.page_info:
            per_page = page_info.per_page
            cur_page = page_info.cur_page
            query = query.limit(per_page).offset((cur_page - 1) * per_page)

        data = [dict(zip([column.name for column in base_table.columns], data)) for data in query.all()]
        result = {
            "result": 1,
            "errorMessage": "",
            "data": data if data else [],
            "header": get_column_info(session, base_table.name),
            "count": count if count else 0,
        }

    except Exception as e:
        result = {"result": 0, "errorMessage": str(e)}
        raise e

    return result


def str_to_filter(key: Column, value: Union[str, int], compare: str):
    compare = compare.lower()
    if compare in ["equal", "="]:
        return key == value
    elif compare == ["not equal", "!="]:
        return key != value
    elif compare == ["greater than", ">"]:
        return key > value
    elif compare == "greater than or equal":
        return key >= value
    elif compare == "less than":
        return key < value
    elif compare == "less than or equal":
        return key <= value
    elif compare == "like":
        return key.like(value)
    elif compare == "not like":
        return not_(key.like(value))
    elif compare == "in":
        return key.in_(value.split(","))
    elif compare == "not in":
        return not_(key.in_(value.split(",")))
    elif compare == "ilike":
        return key.ilike(value)
    else:
        return


def get_column_info(session, table_nm):
    tbl_item_coln_dtl = db.get_table("tbl_item_coln_dtl")
    tbl_item_bas = db.get_table("tbl_item_bas")
    data = (
        session.query(getattr(tbl_item_coln_dtl.columns, "eng_nm"), getattr(tbl_item_coln_dtl.columns, "kor_nm"))
        .join(tbl_item_bas, getattr(tbl_item_bas.columns, "tbl_id") == getattr(tbl_item_coln_dtl.columns, "tbl_id"))
        .filter(getattr(tbl_item_bas.columns, "tbl_nm") == table_nm)
        .all()
    )
    return [dict(zip(["column_name", "kor_column_name"], row)) for row in data]
