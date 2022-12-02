from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.logger import logger

from .utils import ldap_auth, ldap_info
from ServiceUtils.CommonUtil import kt_lamp, knime_encrypt
from ApiService.ApiServiceConfig import config
from .schemas import LoginInfo


# login
async def api(info: LoginInfo, request: Request):
    transaction_id = request.headers.get("transactionId")
    kt_lamp("OUT_REQ", transaction_id, "userLogin")

    try:
        if await ldap_auth(info.id, info.password):
            ldap_user_info = await ldap_info(info.id)

        knime_token = knime_encrypt(info.id + "|^|" + info.password)

        response = JSONResponse(content={"result": 1, "errorMessage": "", "data": {"body": ldap_user_info.dict()}})
        response.set_cookie(
            key=config.secret_info["knime_cookie_name"],
            value=knime_token,
            max_age=3600,
            secure=False,
            httponly=True,
        )
    except Exception as e:
        logger.error(e)
        response = JSONResponse(content={"result": 0, "errorMessage": str(e)})

    kt_lamp("OUT_RES", transaction_id, "userLogin", res_desc=f"{info.id}")
    return response
