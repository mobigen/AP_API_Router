from typing import Union, Optional, List, Dict, Any
from elasticsearch import Elasticsearch


def is_space(text: str) -> int:
    if " " in text:
        result = 1
    else:
        result = 0
    return result


def make_query(operator, field, value) -> Dict[Any, Any]:
    query = {operator: {field: value}}
    return query


def div_keyword(keywords: list) -> Dict[Any, Any]:
    keyword_dict = {"match": []}
    for word in keywords:
        if is_space(word):
            keyword_dict["match"].extend(word.split(" "))
        else:
            keyword_dict["match"].append(word)
    return keyword_dict


def set_dict_list(option_items: Union[list, dict],
                  operator: str, field: Optional[str] = None
                  ) -> List[Dict[Any, Any]]:
    query_list = []
    for item in option_items:
        if field:
            # option_item type list
            query = make_query(operator, field, item)
        else:
            # option item type dict
            query = make_query(operator, item, option_items[item])
        query_list.append(query)
    return query_list


def update_els_data(
    es: Elasticsearch, db_data_list: List[Dict], col_key: str
) -> object:
    """
    CronJob update to elasticsearch index data
    :param es: elasticsearch object
    :param db_data_list: insert data ex) [{col1: val1, col2: val2}, ...]
    :param col_key: data primary key
    :return: elasticsearch helpers object
    """
    els_bulk_items = list()

    for row_data in db_data_list:
        mapping_dict = dict()
        mapping_dict["_id"] = row_data[col_key]
        mapping_dict["_source"] = row_data
        els_bulk_items.append(mapping_dict)

    return es.insert_bulk(els_bulk_items)


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
                    "operator": item.operator
                }
                query = make_query(key,action,words)
                query[key].update(detail)
            else:
                key = "match"
                detail = {
                    action: words,
                    "operator": item.operator
                }
                query = make_query(key, item.field[0], detail)
            # query 추가
            item_dict[sub_action].append(query)
        else:
            continue
    return item_dict