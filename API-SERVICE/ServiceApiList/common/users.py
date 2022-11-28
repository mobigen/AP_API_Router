from typing import Dict
from fastapi.logger import logger
from jose import jwt
from ServiceUtils.CommonUtil import get_exception_info, get_user, get_all_users
from ApiService.ApiServiceConfig import config
from starlette.requests import Request


class InvalidUserInfo(Exception):
    pass


class TokenDoesNotExist(Exception):
    pass


    """
        {
            "user_id": "a0d24b3a-ce8f-4a03-adec-f120ae1d2817",
            "emp_id": "12345678",
            "cmpno": "12345678",
            "user_nm": "홍길동",
            "email": "test@test.com",
            "dept_nm": "데이터사업팀",
            "innt_aut_group_cd": "ROLE_USER",
            "user_type": "SITE_USER",
            "tmp_aut_group_cd": null,
            "tmp_aut_alc_user": null,
            "tmp_aut_alc_date": null,
            "tmp_aut_exp_date": null,
            "exp": 1669597196
        }
    """
def api(request: Request) -> Dict:
    try:
        recv_access_token = request.cookies.get(
            config.secret_info["cookie_name"])
        if not recv_access_token:
            raise TokenDoesNotExist
        payload = jwt.decode(token=recv_access_token,
                             key=config.secret_info["secret_key"], algorithms=config.secret_info["algorithm"])
        username = payload[config.user_info["id_column"]]
        user = get_user(username, "SITE_ADMIN") if payload["user_type"] == "SITE_ADMIN" else None
        if not user:
            raise InvalidUserInfo

        users = get_all_users()

    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = {"result": 1, "errorMessage": "", "data": {"body": users}}

    return result
