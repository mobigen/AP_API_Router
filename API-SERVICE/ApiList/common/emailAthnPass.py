from typing import Dict
from fastapi.logger import logger
from pydantic import BaseModel
from Utils.CommonUtil import get_exception_info, connect_db, convert_data
from ApiService.ApiServiceConfig import config


class EmailAuthFail(Exception):
    pass


class emailAthnPass(BaseModel):
    email: str
    athn_no: str
    new_password: str


def api(email_athn_pass: emailAthnPass) -> Dict:
    user_id = email_athn_pass.email
    new_password = email_athn_pass.new_password
    user_info_table = config.user_info["table"]
    try:
        db = connect_db()
        email_info, _ = db.select(
            f'SELECT * FROM tb_email_athn_info WHERE email={convert_data(email_athn_pass.email)}')

        if email_info[0]["athn_no"] == email_athn_pass.athn_no:
            time_zone = 'Asia/Seoul'
            db.execute(f"SET TIMEZONE={convert_data(time_zone)}")
            if email_info[0]["athn_yn"] == "Y":
                db.execute(
                    f'UPDATE {user_info_table} SET {config.user_info["password_column"]} = {convert_data(config.pwd_context.hash(new_password))} \
                    WHERE {config.user_info["id_column"]} = {convert_data(user_id)};')
            else:
                raise EmailAuthFail
        else:
            raise EmailAuthFail
        logger.info("Successfully Auth Password.")
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = {"result": 1, "errorMessage": ""}

    return result
