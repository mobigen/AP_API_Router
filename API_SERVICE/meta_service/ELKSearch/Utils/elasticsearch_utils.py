import re
import string
from typing import Dict, Any
from datetime import datetime
from elasticsearch import helpers


def is_space(text: str) -> int:
    if " " in text:
        result = 1
    else:
        result = 0
    return result


def make_query(operator, field, value) -> Dict[Any, Any]:
    query = {operator: {field: value}}
    return query


def search_word_filter(keywords: str):
    words = " ".join(keywords).strip()
    words = re.sub(f"[{string.punctuation}]"," ",words)
    return words


def base_search_query(action: str, sub_action: str, item_list: list, check: bool = True) -> Dict:
    item_dict = {sub_action: []}

    for item in item_list:
        if len(item.keywords):

            words = search_word_filter(item.keywords)

            # field div
            if 1 < len(item.field):
                key = "multi_match"
                detail = {
                    "fields": item.field,
                    "operator": item.operator,
                }

                if check:
                    words = " ".join(item.keywords).strip()
                    detail["type"] = "phrase_prefix"

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


def data_process(category: str, data: dict):
    els_dict = dict()
    if category != "data":
        if data["upd_pam_date"]:
            data["upd_pam_date"] = datetime.strptime(data["upd_pam_date"], '%Y-%m-%d')
    els_dict["_id"] = data["biz_dataset_id"]
    els_dict["_source"] = data
    els_dict["_source"]["biz_dataset_id"] = data["biz_dataset_id"]
    return els_dict


def split_insert(es, bulk_meta_item):
    data_size = len(bulk_meta_item)
    batch_size = 500
    if data_size > 500:
        loop = data_size // batch_size
        for i in range(0,loop):
            min_n = i * batch_size
            max_n = (i + 1) * batch_size
            if i == loop - 1:
                max_n = data_size
            helpers.bulk(es.conn, bulk_meta_item[min_n:max_n], index=es.index)
    else:
        helpers.bulk(es.conn, bulk_meta_item, index=es.index)
