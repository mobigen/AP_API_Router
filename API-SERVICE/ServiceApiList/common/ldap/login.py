from datetime import datetime, timedelta
from operator import eq
from pydantic import Field, BaseModel
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from typing import Dict, Optional

from ServiceApiList.common.ldap.utils import run_cmd
from ApiService.ApiServiceConfig import config
from ServiceUtils.CommonUtil import (
    kt_lamp,
    get_exception_info,
    connect_db,
    convert_data,
    create_token,
    make_token_data,
)
from ServiceUtils.crypto import AESCipher


class User(BaseModel):
    emp_id: str = Field(min_length=8, max_length=8, description="emp_id")
    password: str = Field(default=None, description="password")


class UserBas(User):
    user_id: str
    cmpno: str
    user_nm: str
    email: str
    dept_nm: str
    innt_aut_group_cd: Optional[str] = "ROLE_USER"
    sttus: Optional[str] = "SBSC"
    user_type: str

    class Config:
        fields = {"password": {"exclude": True}}


class TmpAuthUserBas(UserBas):
    tmp_aut_group_cd: Optional[str] = None
    tmp_aut_alc_user: Optional[str] = None
    tmp_aut_alc_date: Optional[datetime] = None
    tmp_aut_exp_date: Optional[datetime] = None


def make_insert_query(user: Dict):
    user["reg_user"] = user["user_id"]
    user["reg_date"] = "NOW()"
    columns = ", ".join(user.keys())
    values = ", ".join(map(convert_data, user.values()))
    return f"INSERT INTO user_bas ({columns}) VALUES ({values});"


def knime_encrypt(data: str, key: str):
    return AESCipher(key).encrypt(data).decode()


# login
async def api(user: User, request: Request):
    transaction_id = request.headers.get("transactionId")
    kt_lamp("OUT_REQ", transaction_id, "userLogin")

    try:
        output = await run_cmd(
            config.ldap_info["host"],
            int(config.ldap_info["port"]),
            config.ldap_info["user"],
            config.ldap_info["password"],
            f"{user.emp_id}/{user.password}",
        )
        output = output.split(" ", 1)

        # 인증 실패
        if output[0] == "false":
            return JSONResponse(content={"result": 0, "errorMessage": output[1]})

        # 인증 성공(but user_bas에 없다면 생성)
        db = connect_db()
        user_info, _ = db.select(f"SELECT * FROM user_bas WHERE emp_id = {convert_data(user.emp_id)};")
        if not user_info:
            time_zone = "Asia/Seoul"
            db.execute(f"SET TIMEZONE={convert_data(time_zone)}")
            login_query = make_insert_query()
            db.execute(login_query)
            user_info = user.dict()
        else:
            user_info = user_info[0]

        token_data = make_token_data(TmpAuthUserBas(**user_info).dict())
        access_token = create_token(
            data=token_data,
            expires_delta=timedelta(minutes=int(config.secret_info["expire_min"])),
            secret_key=config.secret_info["secret_key"],
            algorithm=config.secret_info["algorithm"],
        )

        knime_token = knime_encrypt(
            user.emp_id + "|^|" + user.password,
            config.secret_info["secret_key"],
        )

        print(AESCipher(config.secret_info["secret_key"]).decrypt(knime_token).decode())

        response = JSONResponse(content={"result": 1, "errorMessage": ""})
        response.set_cookie(
            key=config.secret_info["cookie_name"],
            value=access_token,
            max_age=3600,
            secure=False,
            httponly=True,
        )
        response.set_cookie(
            key=config.secret_info["knime_cookie_name"],
            value=knime_token,
            max_age=3600,
            secure=False,
            httponly=True,
        )
    except Exception:
        except_name = get_exception_info()
        response = JSONResponse(content={"result": 0, "errorMessage": except_name})

    kt_lamp("OUT_RES", transaction_id, "userLogin", res_desc=f"{user.emp_id}")
    return response
