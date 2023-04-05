import re
from typing import Dict, Any
from datetime import datetime


def is_space(text: str) -> int:
    if " " in text:
        result = 1
    else:
        result = 0
    return result


def make_query(operator, field, value) -> Dict[Any, Any]:
    query = {operator: {field: value}}
    return query


def base_search_query(action: str, sub_action: str, item_list: list) -> Dict:
    item_dict = {sub_action: []}

    for item in item_list:
        if len(item.keywords):
            words = " ".join(item.keywords).strip()

            # field div
            if 1 < len(item.field):
                key = "multi_match"
                detail = {
                    "fields": item.field,
                    "operator": item.operator,
                    "type": "phrase_prefix",
                }
                query = make_query(key, action, words)
                query[key].update(detail)
            else:
                key = "match"
                detail = {action: words, "operator": item.operator}
                query = make_query(key, item.field[0], detail)
            # query 추가
            item_dict[sub_action].append(query)
        else:
            continue
    return item_dict


def default_process(els_dict, data):
    els_dict["_id"] = data["biz_dataset_id"]
    els_dict["_source"] = data
    els_dict["_source"]["biz_dataset_id"] = data["biz_dataset_id"]
    return els_dict


def data_process(data):
    # D-Ocean Project Function
    els_dict = dict()
    data["re_ctgry"] = re.sub("[ ]", "", str(data["ctgry"]))
    data["re_data_shap"] = re.sub("[ ]", "", str(data["data_shap"]))
    data["re_data_prv_desk"] = re.sub("[ ]", "", str(data["data_prv_desk"]))
    if len(data["updt_dt"]) > 26:
        data["updt_dt"] = datetime.strptime(data["updt_dt"][:-3], "%Y-%m-%d %H:%M:%S.%f")

    els_dict = default_process(els_dict, data)
    return els_dict
