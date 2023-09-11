from typing import Dict
from fastapi.logger import logger
from pydantic import BaseModel
from Utils.CommonUtil import get_exception_info, connect_db, convert_data


class EmailAuthFail(Exception):
    pass


class EmailAthnCnfm(BaseModel):
    email: str
    athn_no: str


def api(email_confirm: EmailAthnCnfm) -> Dict:
    try:
        db = connect_db()
        email_info, _ = db.select(
            f"SELECT * FROM tb_email_athn_info WHERE email={convert_data(email_confirm.email)}"
        )

        if email_info[0]["athn_no"] == email_confirm.athn_no:
            time_zone = "Asia/Seoul"
            db.execute(f"SET TIMEZONE={convert_data(time_zone)}")
            db.execute(
                f"UPDATE tb_email_athn_info \
                    SET athn_yn='Y', athn_date=NOW() WHERE email={convert_data(email_confirm.email)};"
            )
        else:
            raise EmailAuthFail
        logger.info("Successfully Auth Confirm.")
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = {"result": 1, "errorMessage": ""}

    return result

