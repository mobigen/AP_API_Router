import random
import string
from typing import Dict

from fastapi.logger import logger
from pydantic import BaseModel

from ApiService.ApiServiceConfig import config
from Utils import insert_mail_history
from Utils.CommonUtil import (
    get_exception_info,
    connect_db,
    convert_data,
    send_template_mail,
)


class EmailNotAuth(Exception):
    pass


class EmailNotExist(Exception):
    pass


class EmailAthnSend(BaseModel):
    email: str
    msg_type: str  # register or password


def make_auth_no():
    string_pool = string.ascii_letters + string.digits
    auth_no = ""
    for _ in range(int(config.email_auth["auth_no_len"])):
        auth_no += random.choice(string_pool)
    return auth_no


def make_email_auth_query(email, auth_no, exist_mail):
    if exist_mail:
        query = f"UPDATE tb_email_athn_info \
                    SET athn_no={convert_data(auth_no)}, send_date=NOW() WHERE email={convert_data(email)};"
    else:
        query = f"INSERT INTO tb_email_athn_info (email, athn_no, athn_yn, send_date) \
                        VALUES ({convert_data(email)}, {convert_data(auth_no)}, 'N', NOW());"
    return query


def api(email_auth: EmailAthnSend) -> Dict:
    try:
        auth_no = make_auth_no()
        db = connect_db()
        exist_mail, _ = db.select(f"SELECT * FROM tb_email_athn_info WHERE email={convert_data(email_auth.email)}")

        if email_auth.msg_type == "password":
            if len(exist_mail) == 0:
                raise EmailNotExist
            if exist_mail[0]["athn_yn"] == "N":
                raise EmailNotAuth

        send_template_mail(auth_no, email_auth.email, email_auth.msg_type)
        insert_mail_history(
            rcv_adr=email_auth.email,
            title=config.email_auth[f"subject_{email_auth.msg_type}"],
            contents=auth_no,
            tmplt_cd=email_auth.msg_type,
        )

        time_zone = "Asia/Seoul"
        db.execute(f"SET TIMEZONE={convert_data(time_zone)}")
        query = make_email_auth_query(email_auth.email, auth_no, exist_mail)
        db.execute(query)

        logger.info("Successfully sent the mail.")
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = {"result": 1, "errorMessage": ""}

    return result
