from typing import Dict

from regex import P
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_token_info, make_res_msg
from Utils.DataBaseUtil import convert_data
from pydantic import BaseModel
from fastapi.logger import logger
from starlette.requests import Request


def api(request: Request) -> Dict:
    user_info = get_token_info(request.headers)

    get_category_list = "SELECT * FROM tb_category;"

    try:
        db = connect_db(config.db_info)
        category_list, _ = db.select(get_category_list)

        node_dict = {}
        category_tree = {}
        for category in category_list:
            node_dict[category["node_id"]] = category["node_nm"]
            category_tree[category["node_nm"]] = []

        for category in category_list:
            if node_dict.get(category["prnts_id"]):
                parent_name = node_dict[category["prnts_id"]]
                category_tree[parent_name].append(category["node_nm"])

        result_category = {}
        for category in category_tree["ROOT"]:
            if category == "ROOT":
                continue
            result_category[category] = None

        for main_category, sub_category in category_tree.items():
            if sub_category:
                if main_category == "ROOT":
                    continue
                result_category[main_category] = sub_category
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        result = make_res_msg(1, "", result_category, [])

    return result
