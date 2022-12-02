from fastapi.logger import logger
from fastapi.responses import JSONResponse
from datetime import timedelta

from ServiceUtils.CommonUtil import (
    make_token_data,
    create_token,
    connect_db,
    convert_data,
)
from .otp_store import OTP
from ServiceUtils.exceptions import InvalidUserInfo
from ApiService.ApiServiceConfig import config
from .schemas import TmpAuthUserBas


class OTPMissMatch(Exception):
    ...


def api(id: str, otp: str):
    try:
        is_ok = OTP.check_otp(id, otp)
        if not is_ok:
            raise OTPMissMatch(f"invalid OTP :: {otp}")

        db = connect_db()
        user_info, _ = db.select(f"SELECT * FROM user_bas WHERE emp_id = {convert_data(id)};")
        if not user_info:
            raise InvalidUserInfo
        user_info = user_info[0]
        token_data = make_token_data(TmpAuthUserBas(**user_info).dict(by_alias=True))
        access_token = create_token(
            data=token_data,
            expires_delta=timedelta(minutes=int(config.secret_info["expire_min"])),
            secret_key=config.secret_info["secret_key"],
            algorithm=config.secret_info["algorithm"],
        )

        response = JSONResponse(content={"result": 1, "errorMessage": ""})
        response.set_cookie(
            key=config.secret_info["cookie_name"],
            value=access_token,
            max_age=3600,
            secure=False,
            httponly=True,
        )
    except Exception as e:
        logger.error(e)
        response = JSONResponse(content={"result": 0, "errorMessage": str(e)})

    return response
