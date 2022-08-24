from typing import Union, Optional, List, Dict, Any
from Utils.DataBaseUtil import convert_data


def is_space(text: str) -> int:
    if " " in text:
        return 1
    else:
        return 0


def make_query(op, field, value) -> Dict[Any,Any]:
    query = {op: {field: value}}
    return query


def div_keyword(keyword_list: list) -> Dict[Any,Any]:
    keyword_dict = {"match_phrase": [], "match": []}
    for keyword in keyword_list:
        k = keyword.replace(" ","")
        if len(k) < 1:
            continue
        if is_space(keyword):
            keyword_dict["match_phrase"].append(keyword)
        else:
            keyword_dict["match"].append(keyword)
    return keyword_dict


def set_find_option(find_option: str) -> List[Dict[Any, Any]]:
    """
    :param find_option: type str, ex) "key1:val1,key2:val2"
    :return: type list , ex) [{key1: val1, key2: val2}]
    """
    find_option = find_option.replace("score", "_score").split(",")
    find_option = [{key: value for key, value in [option_item.split(":") for option_item in find_option]}]
    return find_option


def set_dict_list(option_items: Union[list, dict],
                  operator: str, field: Optional[str] = None
                  ) -> List[Dict[Any, Any]]:
    query_list = []
    for item in option_items:
        if field:
            # option_item type list
            query = make_query(operator,field,item)
        else:
            # option item type dict
            query = make_query(operator,item,option_items[item])
        query_list.append(query)
    return query_list


def update_els_data(db: object, es: object, st: str, et: str) -> None:
    """
    CronJob update to elasticsearch index data
    :param db: postgresql db connector object
    :param es: elasticsearch object
    :param st: start time, type str
    :param et: end time, type str
    :return: None
    """
    db_query = f"SELECT * FROM v_biz_meta_wrap " \
               f"WHERE to_date(updt_date,'YY-MM-DD') " \
               f"BETWEEN {convert_data(st)} AND {convert_data(et)}"

    meta_wrap_list = db.select(db_query)[0]
    bulk_meta_item = list()

    for meta_wrap in meta_wrap_list:
        test_dict = dict()
        test_dict["_id"] = meta_wrap["biz_dataset_id"]
        test_dict["_source"] = meta_wrap
        bulk_meta_item.append(test_dict)

    es.insert_bulk(bulk_meta_item)
