from typing import Dict
from ApiRoute.ApiRouteConfig import config
from Utils.CommonUtil import connect_db


def api(api_name: str) -> Dict:
    db = connect_db(config.db_info)

    return {"API_NAME": "TEST_1"}
