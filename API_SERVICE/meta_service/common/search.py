from meta_service.ELKSearch.Utils.base import set_els, make_format
from meta_service.ELKSearch.document import DocumentManager


def default_search_set(server_config, index, size=10, from_=0):
    es = set_els(server_config)
    docmanger = DocumentManager(es, index)
    docmanger.set_pagination(size, from_)
    return docmanger


def base_query(len_query:int, queryOption: list) -> list:
    """
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
            if len(query.keywords) == 1 else 
            {query_func: {"query": " ".join(query.keywords), "fields": query.field, "operator": query.operator}}
            for query in queryOption
        ]

    else:
        return queryOption
    