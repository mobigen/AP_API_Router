from typing import Dict
from ELKSearch.Manager.manager import ElasticSearchManager
from ELKSearch.Utils.model import InputModel
from ELKSearch.Utils.elasticsearch_utils import make_query, base_search_query
from ELKSearch.Utils.database_utils import get_config
from ServiceUtils.CommonUtil import get_exception_info
from ApiService.ApiServiceConfig import config


def api(input: InputModel) -> Dict:
    els_config = get_config(config.root_path, "config.ini")["kt"]
    data_dict = dict()
    from_ = input.from_ - 1
    data_type = {
        # search_keyword: (result_key, result_data)
        "C": "contentsCount",
        "A": "assetsCount",
        "M": "metaCount",
        "T": "totalCount",
    }
    try:
        es = ElasticSearchManager(page=from_, size=input.size, **els_config)
        es.set_sort(input.sortOption)

        action = "query"
        sub_action = "must"
        for item in input.searchOption:
            if item.field in ["data_nm", "data_desc"]:
                item.field = item.field + ".korean_analyzer"
        query_dict = base_search_query(action, sub_action, input.searchOption)

        sub_action = "filter"
        item_dict = base_search_query(action, sub_action, input.filterOption)
        query_dict.update(item_dict)
        search_query = make_query(action, "bool", query_dict)
        es.body.update(search_query)

        sort_list = [{item.field: item.order} for item in input.sortOption]
        es.set_sort(sort_list)
        search_data = es.search(input.resultField)

        i = None
        for j, item in enumerate(item_dict["filter"]):
            if "data_type" in item["match"].keys():
                i = j
                break
            else:
                i = None

        for key_nm, eng_nm in data_type.items():
            if i is None:
                cnt_query = make_query(
                    "match", "data_type", {"operator": "OR", "query": key_nm}
                )
                item_dict["filter"].append(cnt_query)
                i = -1
            else:
                item_dict["filter"][i]["match"]["data_type"]["query"] = key_nm

            if key_nm == "T":
                del item_dict["filter"][i]

            query_dict.update(item_dict)
            cnt_query = make_query("query", "bool", query_dict)
            cnt = es.conn.count(index=es.index, body=cnt_query)["count"]
            data_dict[eng_nm] = cnt
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        search_list = [data["_source"] for data in search_data["hits"]["hits"]]
        data_dict["searchList"] = search_list
        result = {"result": 1, "errorMessage": "", "data": data_dict}

    return result
