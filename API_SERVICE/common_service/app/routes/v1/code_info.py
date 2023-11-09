import logging

from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from common_service.app.database.conn import db
from libs.database.connector import Executor

logger = logging.getLogger()
router = APIRouter()


@router.get("/getCodeInfo")
async def get_code_detail(groupId, session: Executor = Depends(db.get_db)):
    table_nm = "tb_code_detail"
    rows, _ = session.query(
        table_nm=table_nm,
        where_info=[{"table_nm": table_nm, "key": "code_group_id", "value": groupId, "compare_op": "="}],
    ).all()
    code_infos = [
        {"code_id": row["code_id"], "code_nm": row["code_nm"], "data_1": row["data_1"], "data_2": row["data_2"]}
        if rows
        else []
        for row in rows
    ]

    return JSONResponse(status_code=200, content={"result": 1, "data": {"list": code_infos}, "errorMessage": ""})


@router.get("/getCodeList")
async def get_code_list(
    perPage: int, curPage: int, gropId: str, keyword: str = "", session: Executor = Depends(db.get_db)
) -> JSONResponse:
    table_nm = "tb_code_detail"
    query_data = {
        "table_nm": table_nm,
        "where_info": [{"table_nm": table_nm, "key": "code_group_id", "value": gropId, "compare_op": "="}],
    }

    if keyword:
        # select *, row_number() ... order condition code_nm SIMILAR to %{keyword}% DESC
        query_data["where_info"].append(
            {"table_nm": table_nm, "key": "code_nm", "value": keyword, "compare_op": "like", "op": "AND"}
        )
    else:
        # select *, row_number() ... order condition reg_date ASC
        ...

    query_data["page_info"] = {"per_page": perPage, "cur_page": curPage}
    rows, tcnt = session.query(**query_data).all()

    logger.debug(f"rows :: {rows}, total cnt :: {tcnt}")
    code_info = []
    if rows:
        code_info = [{"code_id": row["code_id"], "code_nm": row["code_nm"]} for row in rows]
        logger.debug(code_info)

    return JSONResponse(
        status_code=200, content={"result": 1, "errorMessage": "", "data": {"totalcount": str(tcnt), "list": code_info}}
    )
