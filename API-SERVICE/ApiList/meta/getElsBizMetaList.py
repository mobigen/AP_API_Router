from typing import Dict
from Utils.CommonUtil import get_exception_info
from Utils.ESUtils import connect_es


def is_space(text:str) -> int:
    if " " in text:
        return 1
    else:
        return 0


def filter_keywords(keywords: list) -> dict:
    keywords_dics = {
        "phrase":[],
        "keywords": []
    }
    for keyword in keywords:
        k = keyword.replace(" ","")
        if len(k) < 1:
            continue
        if is_space(keyword):
            keywords_dics["phrase"].append(keyword)
        else:
            keywords_dics["keywords"].append(keyword)
    return keywords_dics


def make_query(op,field,value):
    query = {op: {field: value}}
    return query


def api(perPage: int = 12,
        curPage: int = 1,
        keyword1: str = "",
        keyword2: str = "",
        keyword3: str = "",
        sort_field: str = "_score",
        sort_order: str = "desc") -> Dict:
    index = "biz_meta"
    curPage = curPage - 1

    body = {
        "from": curPage,
        "size": perPage,
        "sort":[
            # _score는 default 값이 내림차순
            {sort_field: sort_order}
        ],
        "query": {
            "bool": {}
        }
    }
    try:
        es = connect_es()
        keyword_dict = filter_keywords([keyword1,keyword2,keyword3])
        must_query_list = []

        if len(keyword_dict.values()):
            if len(keyword_dict["keywords"]):
                for keyword in keyword_dict["keywords"]:
                    term = make_query("match","data_nm",keyword)
                    must_query_list.append(term)

            if len(keyword_dict["phrase"]):
                for phrase_key in keyword_dict["phrase"]:
                    phrase = make_query("match_phrase","data_nm",phrase_key)
                    must_query_list.append(phrase)
        else:
            query = {"match_all": {}}
            must_query_list.append(query)

        body["query"]["bool"]["must"] = must_query_list
        biz_meta_elk = es.search(index=index,body=body)

    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        search_list = [data["_source"] for data in biz_meta_elk["hits"]["hits"]]
        data = {"totalcount": biz_meta_elk["hits"]["total"]["value"],
                "searchList": search_list}
        result = {"result": 1, "errorMessage": "", "data": data}

    return result
