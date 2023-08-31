import logging
import string
import random
import uuid

from datetime import datetime
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from passlib.context import CryptContext

from libs.database.connector import Executor

from common_service.database.conn import db
from common_service.common.const import (
    EmailSendInfoTable,
    EmailAuthTable,
    UserInfoTable,
    time_zone,
    auth_no_len,
    subject_dict
)


logger = logging.getLogger()
router = APIRouter()


# emailAthnPass
class EmailAuthFail(Exception):
    pass


class EmailAthnPass(BaseModel):
    email: str
    athn_no: str
    new_password: str


# emailAthnSend
class EmailNotAuth(Exception):
    pass


class EmailNotExist(Exception):
    pass


class EmailAthnSend(BaseModel):
    email: str
    msg_type: str  # register or password


# emailAthnCnfm
class EmailAuthFail(Exception):
    pass


class EmailAthnCnfm(BaseModel):
    email: str
    athn_no: str


# emailAthnSend
def make_auth_no():
    string_pool = string.ascii_letters + string.digits
    auth_no = ""
    for _ in range(int(auth_no_len)):
        auth_no += random.choice(string_pool)
    return auth_no


@router.post("/emailAthnPass")
def auth_pass(email_pass: EmailAthnPass, session: Executor = Depends(db.get_db)):
    try:
        email_info = session.query(**EmailAuthTable.get_select_query(email_pass.email)).first()

        if email_info["athn_no"] == email_pass.athn_no and email_info["athn_yn"] == "Y":
            new_password = CryptContext(schemes=["bcrypt"], deprecated="auto").hash(email_pass.new_password)
            user_info = session.query(**UserInfoTable.get_select_query(email_pass.email)).first()
            user_info["user_password"] = new_password
            session.execute(**UserInfoTable.get_execute_query("UPDATE", user_info))
        else:
            raise EmailAuthFail
        result = {"result": 1, "msg": "Successfully Auth Password."}
    except Exception as e:
        result = {"result": 0, "errorMessage": str(e)}
        logger.error(e, exc_info=True)
    return result


@router.post("emailAthnSend")
def auth_send(auth_send: EmailAthnSend, session: Executor = Depends(db.get_db)):
    # todo: insert 구문 축약
    try:
        auth_no = make_auth_no()
        exist_mail = session.query(**EmailAuthTable(auth_send.email)).first()

        if auth_send.msg_type == "password":
            if exist_mail is None:
                raise EmailNotExist
            if exist_mail["athn_yn"] == "N":
                raise EmailNotAuth

        if exist_mail is None:
            # insert
            method = "INSERT"
            exist_mail = {
                "email": auth_send.email,
                "athn_no": auth_no,
                "athn_yn": "N",
                "send_date": "NOW()"
            }
        else:
            # update
            method = "UPDATE"
            exist_mail["athn_no"] = auth_no
            exist_mail["send_date"] = "NOW()"

        EmailAuthTable.get_execute_query(method, exist_mail)

        # mail history insert
        history = {
            "email_id": uuid.uuid4(),
            "rcv_adr": auth_send.email,
            "title": subject_dict[auth_send.msg_type],
            "contents": auth_no,
            "tmplt_cd": auth_send.msg_type,
            "sttus": "REQ",
            "reg_date": datetime.now()
        }
        session.execute(**EmailSendInfoTable.get_execute_query("INSERT", history))

        result = {"result": 1, "msg": "Successfully Auth Password."}
    except Exception as e:
        result = {"result": 0, "errorMessage": str(e)}
        logger.error(e, exc_info=True)
    return result


@router.post("/emailAthnCnfm")
def auth_confirm(auth_conf: EmailAthnCnfm, session: Executor = Depends(db.get_db)):
    try:
        email_info = session.query(**EmailAuthTable.get_select_query(auth_conf.email)).first()
        if email_info["athn_no"] == auth_conf.athn_no:
            email_info["athn_yn"] = "Y"
            email_info["athn_date"] = "NOW()"
            session.execute(**EmailAuthTable.get_execute_query("UPDATE",email_info))
        else:
            raise EmailAuthFail

        result = {"result": 1, "msg": "Successfully Auth Confirm."}
    except Exception as e:
        result = {"result": 0, "errorMessage": str(e)}
        logger.error(e, exc_info=True)
    return result
