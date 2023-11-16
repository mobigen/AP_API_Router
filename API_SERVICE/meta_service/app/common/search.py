from datetime import datetime

from pydantic import BaseModel

from libs.els.ELKSearch.Utils.base import set_els, make_format
from libs.els.ELKSearch.document import DocumentManager
from libs.els.ELKSearch.model import InputModel
from meta_service.app.common.config import base_dir


class Record(BaseModel):
    index: str
    key: str
    ids: str


class SearchModel(InputModel):
    chk: bool = False


def exception_col(table_nm: str, insert_body: dict) -> dict:
    """
    db데이터를 els에 넣기전 실행해야 하는 예외 처리
    입력하지 못하는 column들을 insert 구문에서 삭제 해주는 기능
    """
    pass


def default_search_set(host, port, index, size=10, from_=0):
    """
    검색에 필요한 default 세팅
    자동완성과 검색에 사용
    """
    es = set_els(host, port)
    docmanger = DocumentManager(es, index)
    docmanger.set_pagination(size, from_)
    return docmanger


def record_keyword(search_option):
    word_path = f"{base_dir}/log/{datetime.today().strftime('%Y%m%d')}_search.log"
    with open(word_path, "a") as fp:
        for search_query in search_option:
            fp.write(f"{str(search_query.keywords)}\n")


def base_query(len_query: int, queryOption: list) -> list:
    """
    검색에 사용되는 base_query, match must 방식으로 query를 만들어 준다
    :param queryOption: ELKSearch model SearchOption or FilterOption
    :return:
    ["multi_match": {
            "query": "data_1",
            "fields": ["column_1"],
            "type": "phrase_prefix"
        }
    ]
    """
    if len_query:
        query_func = "multi_match"
        query_type = "phrase_prefix"

        return [
            {
                query_func: {
                    "query": str(query.keywords[0]),
                    "fields": query.field,
                    "type": query_type,
                }
            }
            if len(query.keywords) == 1
            else {
                query_func: {
                    "query": " ".join(query.keywords),
                    "fields": query.field,
                    "operator": query.operator,
                }
            }
            for query in queryOption
        ]

    else:
        return queryOption


def delete_srttn(item_list):
    for i, item in enumerate(item_list):
        if "data_srttn" in item.keys():
            del item_list[i]
            break
    return item_list


def check_query(query_dict, item_list):
    if "match_all" in query_dict["query"].keys():
        return make_format("query", "bool", {"filter": item_list}), item_list
    else:
        return query_dict, delete_srttn(item_list)


def search_count(es, item_list, query_dict):
    # data_srttn 순서 고정
    # totalCount에 해외데이터는 포함되지 않는다
    data_srttn = {
        # search_keyword: (result_key, result_data)
        "전체": "totalCount",
        "보유데이터": "hasCount",
        "연동데이터": "innerCount",
        "외부데이터": "externalCount",
        "해외데이터": "overseaCount",
    }
    data_dict = dict()
    index = "biz_meta,v_biz_meta_oversea_els"

    # set query count dict
    query_dict, item_list = check_query(query_dict, item_list)
    srttn_index = len(item_list)
    for ko_nm, eng_nm in data_srttn.items():
        if ko_nm != "전체":
            item_list = item_list[:srttn_index]
            cnt_query = make_format(
                "match", "data_srttn", {"operator": "OR", "query": ko_nm}
            )
            item_list.append(cnt_query)

        query_dict["query"]["bool"]["filter"] = item_list
        es.index = index
        cnt = es.count(body=query_dict)
        data_dict[eng_nm] = cnt

    return data_dict
