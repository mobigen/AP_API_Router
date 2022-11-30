from copy import deepcopy
from typing import Dict
from ELKSearch.Manager.manager import ElasticSearchManager
from ELKSearch.Utils.model import InputModel
from ELKSearch.Utils.elasticsearch_utils import make_query, base_search_query
from ELKSearch.Utils.database_utils import get_config
from ServiceUtils.CommonUtil import get_exception_info
from ApiService.ApiServiceConfig import config


def api(input: InputModel, u_id: str = "") -> Dict:
    index = "kt_biz_data"
    els_config = get_config(config.root_path, "config.ini")[config.db_type[:-3]]
    from_ = input.from_ - 1
    data_dict = dict()

    try:
        es = ElasticSearchManager(
            page=from_, size=input.size, index=index, **els_config
        )
        es.set_sort(input.sortOption)

        action = "query"
        sub_action = "must"
        for item in input.searchOption:
            tmp = []
            for field in item.field:
                if field in ["data_nm", "data_desc"]:
                    col = field + ".korean_analyzer"
                else:
                    col = field
                tmp.append(col)
            item.field = tmp
        query_dict = base_search_query(action, sub_action, input.searchOption)

        sub_action = "filter"
        item_dict = base_search_query(action, sub_action, input.filterOption)
        query_dict.update(item_dict)
        search_query = make_query(action, "bool", query_dict)
        es.body.update(search_query)

        sort_list = [{item.field: item.order} for item in input.sortOption]
        es.set_sort(sort_list)
        search_data = es.search(input.resultField)

        body = deepcopy(es.body)
        del body["sort"]
        data_dict["C"] = es.conn.count(index="kt_biz_asset", body=body)["count"]

        # assets index count n
        data_type = make_query(
            "match", "conts_dataset_reg_yn", {"operator": "OR", "query": "N"}
        )
        body["query"]["bool"]["filter"].append(data_type)
        data_dict["A"] = es.conn.count(index="kt_biz_asset", body=body)["count"]

        # meta index count
        body = deepcopy(es.body)
        del body["sort"]
        data_dict["M"] = es.conn.count(index="kt_biz_data", body=body)["count"]

        data_dict["totalCount"] = sum(data_dict.values())

    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        search_list = [data["_source"] for data in search_data["hits"]["hits"]]
        data_dict["searchList"] = search_list
        result = {"result": 1, "errorMessage": "", "data": data_dict}

    return result
