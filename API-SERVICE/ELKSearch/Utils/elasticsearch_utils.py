from typing import Dict, Any


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
