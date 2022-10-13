from typing import Dict, Optional
from pydantic import BaseModel
from fastapi.logger import logger
from fastapi.responses import JSONResponse
from datetime import timedelta
from ServiceUtils.CommonUtil import get_exception_info, connect_db, convert_data, create_token, make_token_data
from ApiService.ApiServiceConfig import config


class userLogin(BaseModel):
    user_id: str
    emp_id: str
    cmpno: str
    user_nm: str
    email: str
    dept_nm: str
    aut_group_cd: Optional[str] = 'ROLE_USER'
    data_clas_cd: Optional[str] = 'GRADE3'
    sttus: Optional[str] = 'SBSC'


def make_insert_query(login: dict):
    login["reg_user"] = login["user_id"]
    login["reg_date"] = "NOW()"
    columns = ", ".join(login.keys())
    values = ", ".join(map(convert_data, login.values()))
    return f'INSERT INTO user_bas ({columns}) VALUES ({values});'


def api(login: userLogin) -> Dict:
    try:
        db = connect_db()
        user_info, _ = db.select(
            f'SELECT * FROM user_bas WHERE emp_id = {convert_data(login.emp_id)};')
        if not user_info:
            time_zone = 'Asia/Seoul'
            db.execute(f"SET TIMEZONE={convert_data(time_zone)}")
            login_query = make_insert_query(login.__dict__)
            db.execute(login_query)
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        token_data = make_token_data(login.__dict__)
        access_token = create_token(
            data=token_data, expires_delta=timedelta(minutes=int(config.secret_info["expire_min"])))
        result = {"result": 1, "errorMessage": ""}

    response = JSONResponse(content=result)
    response.set_cookie(
        key=config.secret_info["cookie_name"], value=access_token)
    return response
