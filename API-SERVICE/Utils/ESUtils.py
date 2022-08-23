def is_space(text: str) -> int:
    if " " in text:
        return 1
    else:
        return 0


def make_query(op, field, value):
    query = {op: {field: value}}
    return query


def div_keyword(keyword_list: list) -> dict:
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


def set_find_option(find_option: str) -> list:
    """
    :param find_option: type str, ex) "key1:val1,key2:val2"
    :return: type list , ex) [{key1: val1, key2: val2}]
    """
    find_option = find_option.replace("score", "_score").split(",")
    find_option = [{key: value for key, value in [option_item.split(":") for option_item in find_option]}]
    return find_option


def set_dict_list(item_list, operator, field=None):
    query_list = []
    for item in item_list:
        if field:
            query = make_query(operator,field,item)
        else:
            query = make_query(operator,item,item_list[item])
        query_list.append(query)
    return query_list

