from .otp_store import OTP
from .utils import ldap_info
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.logger import logger

from ApiService.ApiServiceConfig import config
from ServiceUtils.CommonUtil import knime_decrpyt
from ServiceUtils.exceptions import TokenDoesNotExist, InvalidUserInfo


async def api(id: str, request: Request):
    try:
        if config.secret_info["knime_cookie_name"] in request.cookies:
            token = request.cookies[config.secret_info["knime_cookie_name"]]
            data = knime_decrpyt(token)
            if id not in data:
                raise InvalidUserInfo(f"user {id} not authenticate")
        else:
            raise TokenDoesNotExist("TokenDoesNotExist")

        ldap_user_info = await ldap_info(id)
        mobile = ldap_user_info.mobile
        otp = OTP.create()
        OTP.add_otp(id, otp)

        # sms to mobile
        # TODO: ldap insert to table
        """
            insert into sdk_sms_send
                (user_id, schedule_type, subject, sms_msg, callback_url, now_date, send_date, callback, dest_info, reserved1, reserved2)
            values
                    ('ktsaup0519', '0', 'otp', '[사내접근제어 DOCEAN] 인증번호 [123456] 입니다. 3분안에 입력해주세요.', null,
                    date_format(now(), '%Y%m%d%H%i%S'), date_format(now()+2, '%Y%m%d%H%i%S'),
                    '15883391', '양석우', '01099858980', '991456', '91312828');
        """

        logger.info(f"CREATE OTP :: {otp}")
        response = JSONResponse(content={"result": 1, "errorMessage": ""})
    except Exception as e:
        logger.error(e)
        response = JSONResponse(content={"result": 0, "errorMessage": str(e)})

    return response
