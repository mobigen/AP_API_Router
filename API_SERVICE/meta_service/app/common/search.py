from fastapi.logger import logger
from pydantic import BaseModel

from meta_service.app.ELKSearch.Utils.base import set_els
from meta_service.app.ELKSearch.document import DocumentManager


class Upsert(BaseModel):
    index: str
    key: str
    ids: str


def exception_col(table_nm: str, insert_body: dict) -> dict:
    """
    db데이터를 els에 넣기전 실행해야 하는 예외 처리
    입력하지 못하는 column들을 insert 구문에서 삭제 해주는 기능
    """

    if table_nm == "vw_co_if":
        insert_body.pop("mjrdfnprdc", None)
        insert_body.pop("mjrcvlprdc", None)
        insert_body.pop("skl", None)
    if table_nm == "vw_expr_item_db":
        logger.info(insert_body.keys())
        for key in list(insert_body.keys()):
            if not key in ["idx", "korconm"]:
                insert_body.pop(key, None)
    return insert_body


def default_search_set(server_config, index, size=10, from_=0):
    """
    검색에 필요한 default 세팅
    자동완성과 검색에 사용
    """
    es = set_els(server_config)
    docmanger = DocumentManager(es, index)
    docmanger.set_pagination(size, from_)
    return docmanger


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
            {query_func: {"query": str(query.keywords[0]), "fields": query.field, "type": query_type}}
            if len(query.keywords) == 1
            else {query_func: {"query": " ".join(query.keywords), "fields": query.field, "operator": query.operator}}
            for query in queryOption
        ]

    else:
        return queryOption
