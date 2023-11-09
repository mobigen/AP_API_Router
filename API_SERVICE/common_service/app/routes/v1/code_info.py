from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from common_service.app.database.conn import db
from libs.database.connector import Executor

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
