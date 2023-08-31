import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from passlib.context import CryptContext

from common_service.database.conn import db
from common_service.common.const import EmailAuthTable, UserInfoTable, time_zone

from libs.database.connector import Executor


logger = logging.getLogger()
router = APIRouter()


# emailAthnPass.py
class EmailAuthFail(Exception):
    pass


class EmailAthnPass(BaseModel):
    email: str
    athn_no: str
    new_password: str


@router.post("/emailAthnPass")
def auth_pass(email_pass: EmailAthnPass, session: Executor = Depends(db.get_db)):
    try:
        email_info = session.query(**EmailAuthTable.get_select_query(email_pass.email)).first()

        if email_info["athn_no"] == email_pass.athn_no and email_info["athn_yn"] == "Y":
            new_password = CryptContext(schemes=["bcrypt"], deprecated="auto").hash(email_pass.new_password)
            user_info = session.query(**UserInfoTable.get_select_query(email_pass.email)).first()
            user_info["user_password"] = new_password
            session.execute(**UserInfoTable.get_update_query(user_info))
        else:
            raise EmailAuthFail
        result = {"result": 1, "msg": "Successfully Auth Password."}
    except Exception as e:
        result = {"result": 0, "errorMessage": str(e)}
        logger.error(e, exc_info=True)
    return result


