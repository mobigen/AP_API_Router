from typing import Dict
from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from libs.database.connector import Executor
from common_service.database.conn import db

router = APIRouter()


@router.get("/getCodeInfo")
async def get_code_detail(groupId, session: Executor = Depends(db.get_db)) -> Dict:
    rows, _ = session.query(table_nm="tb_code_detail", key="code_group_id", value=groupId).all()
    code_infos = [
        {"code_id": row["code_id"], "code_nm": row["code_nm"], "data_1": row["data_1"], "data_2": row["data_2"]}
        if rows
        else []
        for row in rows
    ]

    return JSONResponse(status_code=200, content={"result": 1, "data": code_infos, "errorMessage": ""})
