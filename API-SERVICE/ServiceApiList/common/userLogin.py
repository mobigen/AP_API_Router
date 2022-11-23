from typing import Dict, Optional
from pydantic import BaseModel
from fastapi import Request
from fastapi.logger import logger
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from ServiceUtils.CommonUtil import get_exception_info, connect_db, convert_data, create_token, make_token_data, kt_lamp
from ApiService.ApiServiceConfig import config
from ServiceUtils.crypto import AESCipher


class userLogin(BaseModel):
    """
        {
            "user_id":"e2851973-2239-4a44-8feb-00d5a3fb23ef",
            "emp_id":"11181059",
            "cmpno":"11181059",
            "user_nm":"swyang",
            "email":"swyang",
            "dept_nm":"swyang",
            "user_type":"SITE_USER"
        }
    """
    user_id: str
    password: str = "1234"
    emp_id: str
    cmpno: str
    user_nm: str
    email: str
    dept_nm: str
    innt_aut_group_cd: Optional[str] = 'ROLE_USER'
    sttus: Optional[str] = 'SBSC'
    user_type: str

    class Config:
        fields = {"password": {"exclude": True}}

class TmpAuthUser(userLogin):
    tmp_aut_group_cd: Optional[str] = None
    tmp_aut_alc_user: Optional[str] = None
    tmp_aut_alc_date: Optional[datetime] = None
    tmp_aut_exp_date: Optional[datetime] = None



def make_insert_query(login: dict):
    login["reg_user"] = login["user_id"]
    login["reg_date"] = "NOW()"
    columns = ", ".join(login.keys())
    values = ", ".join(map(convert_data, login.values()))
    return f'INSERT INTO user_bas ({columns}) VALUES ({values});'


def api(login: userLogin, request: Request) -> Dict:
    transaction_id = request.headers.get("transactionId")
    kt_lamp("OUT_REQ", transaction_id, "userLogin")

    try:
        db = connect_db()
        user_info, _ = db.select(
            f'SELECT * FROM user_bas WHERE emp_id = {convert_data(login.emp_id)};')
        if not user_info:
            time_zone = 'Asia/Seoul'
            db.execute(f"SET TIMEZONE={convert_data(time_zone)}")
            login_query = make_insert_query(login.dict())
            db.execute(login_query)
            user_info = login.dict()
        else:
            user_info = user_info[0]
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
        # kt_lamp("OUT_RES", "userLogin", res_type="S",`
        #        res_code = "DC_ERROR", res_desc = f'{login.emp_id}.{except_name}')
    else:
        token_data = make_token_data(TmpAuthUser(**user_info).dict())
        access_token = create_token(
            data=token_data,
            expires_delta=timedelta(minutes=int(config.secret_info["expire_min"])),
            secret_key=config.secret_info["secret_key"],
            algorithm=config.secret_info["algorithm"]
        )

        knime_token = knime_encrypt(login.user_id + "|^|" + login.password, config.secret_info["knime_secret_key"])

        result = {"result": 1, "errorMessage": ""}

    response = JSONResponse(content=result)
    response.set_cookie(
        key=config.secret_info["cookie_name"], value=access_token, max_age=3600, secure=False, httponly=True)
    response.set_cookie(
        key=config.secret_info["knime_cookie_name"], value=knime_token, max_age=3600, secure=False, httponly=True)

    kt_lamp("OUT_RES", transaction_id, "userLogin",
            res_desc=f'{login.emp_id}')
    return response


def knime_encrypt(data: str, key: str):
    return AESCipher(key).encrypt(data).decode()


