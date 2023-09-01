import json
import string
import random
import requests
from typing import Dict
from Utils.CommonUtil import get_exception_info, connect_db
from fastapi.logger import logger


base_url = "https://b-iris.mobigen.com"


def get_token(iris_info, header):
    iris_id = iris_info[0]["iris_id"]
    iris_pw = iris_info[0]["iris_pw"]
    login_iris = {
        "userId": iris_id,
        "userPass": iris_pw
    }
    res = requests.post(f"{base_url}/authenticate",data=json.dumps(login_iris), verify=False, headers=header)

    return res.json()


def get_random_str(is_num: bool) -> str:
    """
    :param is_num:
        - is_num이 True이면 10자리 숫자를 임의로 반환
        - False이면 5자리 영문자를 랜덤하게 반환
    :return:
    """
    if is_num:
        result = [str(random.randrange(0,9)) for _ in range(0,5)]
    else:
        result = [random.choice(string.ascii_lowercase) for _ in range(0,5)]
    return "".join(result)


# get
def api(user_id: str) -> Dict:
    iris_query = f"select * from users.tb_iris_user_info where user_id = '{user_id}'"
    header = {"Content-Type": "application/json"}
    try:
        db = connect_db()
        # join check
        iris_info = db.select(iris_query)[0]

        # join iris
        if not len(iris_info):
            # get user info
            user_query = f"select * from users.tb_user_info where user_id = '{user_id}'"
            user_info = db.select(user_query)[0][0]

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
                dup_query = f"select * from users.tb_iris_user_info where iris_id = '{iris_id}'"
                dup_check = db.select(dup_query)[0]
                logger.info(dup_check)
                if not len(dup_check):
                    logger.info("break")
                    break
            # insert 구문
            insert_query = f"INSERT INTO users.tb_iris_user_info (user_id, iris_id, iris_pw) " \
                           f"VALUES {user_id, iris_id, iris_pw};"
            logger.info(insert_query)
            logger.info(db.execute(insert_query))

            join_info = {
                "userId": iris_id,
                "userPass": iris_pw,
                "roleCode": "USER",
                "groupId": "62b3fa2f-f3f5-4f88-a6de-dfef48c5c37a", # Default Group
                "name": user_info["user_nm"],
                "desc": "테스트용 아이디",
                "email": user_id,
                "phone": user_info["moblphon"]
            }
            logger.info(join_info)

            # login
            iris_root = [{
                "iris_id": "root",
                "iris_pw": "!dufmaQkdgkr202208"
            }]
            root_token = get_token(iris_root, header)["token"]
            header["x-access-token"] = root_token

            logger.info(root_token)
            logger.info(header)

            res = requests.post(f"{base_url}/meta/account",data=json.dumps(join_info), verify=False, headers=header)
            logger.info(res.text)

            del header["x-access-token"]

        iris_info = db.select(iris_query)[0]
        logger.info(iris_info)
        user_token = get_token(iris_info, header)

        result = {"result": 1, "errorMessage": "", "data": user_token}
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}

    return result