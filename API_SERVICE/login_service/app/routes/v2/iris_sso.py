import json
import logging
import random
import string
import sys
import traceback
from ast import literal_eval

import requests
from fastapi import APIRouter, Depends, Request
from starlette.responses import JSONResponse

from libs.auth.keycloak import keycloak
from libs.database.connector import Executor
from login_service.app.common.config import settings
from login_service.app.common.const import COOKIE_NAME, LoginTable, IrisInfoTable
from login_service.app.database.conn import db

logger = logging.getLogger()
router = APIRouter()


def get_exception_info():
    ex_type, ex_value, ex_traceback = sys.exc_info()
    trace_back = traceback.extract_tb(ex_traceback)
    trace_log = "\n".join([str(trace) for trace in trace_back])
    logger.error(
        f"\n- Exception Type : {ex_type}\n- Exception Message : {str(ex_value).strip()}\n- Exception Log : \n{trace_log}"
    )
    return ex_type.__name__


def get_token(iris_info, header):
    iris_id = iris_info[0]["iris_id"]
    iris_pw = iris_info[0]["iris_pw"]
    login_iris = {"userId": iris_id, "userPass": iris_pw}
    res = requests.post(f"{settings.IRIS_INFO.IRIS_DOMAIN}/authenticate", data=json.dumps(login_iris), verify=False, headers=header)

    return res.json()


def get_random_str(is_num: bool) -> str:
    """
    :param is_num:
        - is_num이 True이면 10자리 숫자를 임의로 반환
        - False이면 5자리 영문자를 랜덤하게 반환
    :return:
    """
    if is_num:
        result = [str(random.randrange(0, 9)) for _ in range(0, 5)]
    else:
        result = [random.choice(string.ascii_lowercase) for _ in range(0, 5)]
    return "".join(result)


@router.get("/user/v2/ConnectIRIS")
async def api(request: Request, session: Executor = Depends(db.get_db)) -> JSONResponse:
    header = {"Content-Type": "application/json"}
    token = request.cookies.get(COOKIE_NAME)

    if not token:
        msg = "TokenDoesNotExist"
        logger.info(msg)
        return JSONResponse(status_code=200, content={"result": 0, "errorMessage": msg})

    token = literal_eval(token)
    userInfo = await keycloak.user_info(token=token["data"]["access_token"], realm=settings.KEYCLOAK_INFO.REALM)
    if userInfo.get("status_code") != 200:
        return JSONResponse(
            status_code=400, content={"result": 0, "errorMessage": userInfo.get("data").get("error_description")}
        )

    user_id = userInfo.get("data").get("user_id")

    iris_table = IrisInfoTable()
    try:
        # join check
        iris_info = session.query(**iris_table.get_query_data(user_id)).first()

        # join iris
        if iris_info is None:
            # get user info
            user_info = session.query(**LoginTable.get_query_data(user_id)).first()

            # set iris id pw
            while True:
                pw = get_random_str(False)
                iris_pw = f"{pw[0].upper()}{pw[1:]}-{get_random_str(True)}"
                iris_id = f"katech{get_random_str(False)}{get_random_str(True)}"

                logger.info("=== CREATE USER ID,PW ===")
                logger.info(f"IRIS ID : {iris_id}")
                logger.info(f"IRIS PW : {iris_pw}")
                logger.info("==========================")

                # check duplicate iris_id
                iris_table.key_column = "iris_id"
                dup_check = session.query(**iris_table.get_query_data(iris_id)).first()
                logger.info(dup_check)

                if dup_check is None:
                    logger.info("break")
                    break
            # insert 구문
            insert_query = {"user_id": user_id, "iris_id": iris_id, "iris_pw": iris_pw}
            logger.info(session.execute(**iris_table.upsert_query_data("INSERT", insert_query)))

            # iris join API
            join_info = {
                "userId": iris_id,
                "userPass": iris_pw,
                "roleCode": "USER",
                "groupId": "62b3fa2f-f3f5-4f88-a6de-dfef48c5c37a",  # Default Group
                "name": user_info["user_nm"],
                "desc": "테스트용 아이디",
                "email": user_id,
                "phone": user_info["moblphon"],
            }
            logger.info(join_info)

            # login

            iris_root = [{"iris_id": settings.IRIS_INFO.IRIS_ROOT_USER, "iris_pw": settings.IRIS_INFO.IRIS_ROOT_PASS}]  # "Katech12#$"
            root_token = get_token(iris_root, header)["token"]
            header["x-access-token"] = root_token

            logger.info(root_token)
            logger.info(header)

            res = requests.post(f"{settings.IRIS_INFO.IRIS_DOMAIN}/meta/account", data=json.dumps(join_info), verify=False, headers=header)
            logger.info(res.text)

            iris_table.key_column = "user_id"
            del header["x-access-token"]

        iris_info = session.query(**iris_table.get_query_data(user_id)).first()
        user_token = get_token([iris_info], header)

        result = JSONResponse(status_code=200, content={"result": 1, "errorMessage": "", "data": user_token})
    except Exception:
        except_name = get_exception_info()
        result = JSONResponse(status_code=400, content={"result": 0, "errorMessage": except_name})

    return result
