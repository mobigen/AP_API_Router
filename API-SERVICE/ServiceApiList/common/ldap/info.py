from fastapi.requests import Request
from fastapi.logger import logger
from fastapi.responses import JSONResponse

from ServiceUtils import CommonUtil as utils
from .utils import ldap_info


async def api(request: Request):
    try:
        user = utils.get_user_info(request)
        ldap_user_info = await ldap_info(user["cmpno"])

        response = JSONResponse(content={"result": 1, "errorMessage": "", "data": {"body": ldap_user_info.dict()}})
    except Exception as e:
        logger.error(e)
        response = JSONResponse(content={"result": 0, "errorMessage": str(e)})
    return response
