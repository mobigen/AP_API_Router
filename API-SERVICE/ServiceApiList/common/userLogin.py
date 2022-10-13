from typing import Dict, Optional
from pydantic import BaseModel
from fastapi.logger import logger
from fastapi.responses import JSONResponse
from datetime import timedelta
from ServiceUtils.CommonUtil import get_exception_info, connect_db, convert_data, create_token, make_token_data, authenticate_user
from ApiService.ApiServiceConfig import config


class userLogin(BaseModel):
    user_id: str
    emp_id: str
    cmpno: str
    user_nm: str
    email: str
    aut_group_cd: Optional[str] = 'ROLE_USER'
    data_clas_cd: Optional[str] = 'GRADE3'
    #amd_user: Optional[str] = ''
    #amd_date: Optional[str] = None
    sttus: Optional[str] = 'SBSC'


'''

user_id => uuid 랜덤값
emp_id => 사원 아이디(로그인아이디)
cmpno => 사번
user_nm => 사원 이름
email => 사원 이메일
aut_group_cd => ROLE_USER
data_clas_cd => GRADE3
reg_user => user_id와 동일한 값
reg_date => 현재시간
amd_user => null
amd_date => null
sttus => SBSC
'''


def make_insert_query(login: dict):
    print(f'Login Data : {login}, type : {type(login)}')
    login["reg_user"] = login["user_id"]
    login["reg_date"] = "NOW()"
    columns = ", ".join(login.keys())
    values = ", ".join(map(convert_data, login.values()))
    print(f'INSERT INTO user_bas ({columns}) VALUES ({values});')
    return f'INSERT INTO user_bas ({columns}) VALUES ({values});'


def api(login: userLogin) -> Dict:
    try:
        db = connect_db()
        time_zone = 'Asia/Seoul'
        db.execute(f"SET TIMEZONE={convert_data(time_zone)}")
        login_query = make_insert_query(login.__dict__)
        db.execute(login_query)
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:

        result = {"result": 1, "errorMessage": ""}

    return result
