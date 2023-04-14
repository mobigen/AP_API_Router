from typing import Dict, List, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from common_service.database.conn import db


class CommonExecute(BaseModel):
    method: str
    table_nm: str
    data: Dict
    key: Optional[List[str]] = None


router = APIRouter()


@router.post("/common-execute")
async def common_execute(params: List[CommonExecute], session: Session = Depends(db.get_db)):
    """
        [
            {
                "method":"INSERT",
                "table_nm":"inqr_bas",
                "data":{
                    "id":"9bb29b2b-159e-4cee-89af-a80cfe6f0651",
                    "title":"test문의",
                    "sbst":"문으으으의",
                    "ctg_id":"INQR001",
                    "reg_user_nm":"테스터",
                    "cmpno":"dev-12346578",
                    "del_yn":"N",
                    "reg_user":"f142cdc2-207b-4eda-9e7d-2605e4e65571",
                    "reg_date":"NOW()",
                    "amd_user":"f142cdc2-207b-4eda-9e7d-2605e4e65571",
                    "amd_date":"NOW()"
                }
            }
        ]
        [
            {
                "method":"UPDATE",
                "table_nm":"inqr_bas",
                "key": ["id"],
                "data":{
                    "id":"9bb29b2b-159e-4cee-89af-a80cfe6f0651",
                    "title":"test문의111111",
                    "sbst":"문으으으의"
                }
            }
        ]
        [
            {
                "method":"DELETE",
                "table_nm":"inqr_bas",
                "key": ["id"],
                "data":{
                    "id":"9bb29b2b-159e-4cee-89af-a80cfe6f0651"
                }
            }
        ]

        {"result":1,"errorMessage":""}
    """
    try:
        session.begin()

        for row in params:
            method = row.method.lower()
            table = db.get_table(row.table_nm)
            cond = [getattr(table.columns, k) == row.data[k] for k in row.key] if row.key else []

            if method == "insert":
                ins = table.insert().values(**row.data)
                session.execute(ins)
            elif method == "update":
                stmt = table.update().where(*cond).values(**row.data)
                session.execute(stmt)
            elif method == "delete":
                stmt = table.delete().where(*cond)
                session.execute(stmt)
            else:
                raise NotImplementedError

        session.commit()
    except Exception as e:
        session.rollback()
        raise e
