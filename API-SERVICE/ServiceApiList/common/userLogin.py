from typing import Dict, Optional
from pydantic import BaseModel
from fastapi import Request
from fastapi.logger import logger
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from ServiceUtils.CommonUtil import get_exception_info, connect_db, convert_data, create_token, make_token_data, kt_lamp
from ApiService.ApiServiceConfig import config


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
    emp_id: str
    cmpno: str
    user_nm: str
    email: str
    dept_nm: str
    tmp_aut_group_cd: Optional[str] = 'ROLE_USER'
    tmp_aut_alc_user: str = ""
    tmp_aut_alc_date: datetime = datetime.now()
    tmp_aut_exp_date: datetime = datetime.now()
    innt_aut_group_cd: Optional[str] = 'ROLE_USER'
    sttus: Optional[str] = 'SBSC'
    user_type: str


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
            login_query = make_insert_query(login.__dict__)
            db.execute(login_query)
            user_info = login.__dict__
        else:
            user_info = user_info[0]
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
        # kt_lamp("OUT_RES", "userLogin", res_type="S",`
        #        res_code = "DC_ERROR", res_desc = f'{login.emp_id}.{except_name}')
    else:
        token_data = make_token_data(user_info)
        access_token = create_token(
            data=token_data, expires_delta=timedelta(minutes=int(config.secret_info["expire_min"])))
        result = {"result": 1, "errorMessage": ""}

    response = JSONResponse(content=result)
    response.set_cookie(
        key=config.secret_info["cookie_name"], value=access_token, max_age=3600, secure=False, httponly=True)

    kt_lamp("OUT_RES", transaction_id, "userLogin",
            res_desc=f'{login.emp_id}')
    return response
