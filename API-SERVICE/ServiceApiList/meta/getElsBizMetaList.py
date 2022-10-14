from typing import Dict
from ELKSearch.Manager.manager import ElasticSearchManager
from ELKSearch.Utils.model import InputModel
from ELKSearch.Utils.elasticsearch_utils import make_query, base_search_query
from ServiceUtils.CommonUtil import get_exception_info


def api(input: InputModel) -> Dict:
    data_dict = dict()
    from_ = input.from_ - 1

    try:
        es = ElasticSearchManager(page=from_, size=input.size)
        es.set_sort(input.sortOption)

        action = "query"
        sub_action = "must"
        for item in input.searchOption:
            if item.field in ["data_nm", "data_desc"]:
                item.field = item.field + ".korean_analyzer"
        query_dict = base_search_query(action,sub_action,input.searchOption)

        sub_action = "filter"
        item_dict = base_search_query(action,sub_action,input.filterOption)
        query_dict.update(item_dict)
        search_query = make_query(action,"bool", query_dict)
        es.body.update(search_query)

        sort_list = [{item.field: item.order} for item in input.sortOption]
        es.set_sort(sort_list)
        search_data = es.search(input.resultField)

    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        search_list = [data["_source"] for data in search_data["hits"]["hits"]]
        data_dict["searchList"] = search_list
        result = {"result": 1, "errorMessage": "", "data": data_dict}

    return result
