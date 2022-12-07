from copy import deepcopy
from typing import Dict
from datetime import datetime
from ELKSearch.Manager.manager import ElasticSearchManager
from ELKSearch.Utils.model import InputModel
from ELKSearch.Utils.elasticsearch_utils import make_query, base_search_query
from ELKSearch.Utils.database_utils import get_config
from ServiceUtils.CommonUtil import get_exception_info
from ApiService.ApiServiceConfig import config


def api(input: InputModel) -> Dict:
    index = "kt_biz_asset"
    els_config = get_config(config.root_path, "config.ini")[config.db_type[:-3]]
    from_ = input.from_ - 1
    data_dict = dict()

    try:
        if input.chk and len(input.searchOption):
            with open(f"{config.root_path}/log/{config.category}/{datetime.today().strftime('%Y%m%d')}_search.log","a") as fp:
                for search in input.searchOption:
                    fp.write(f"{str(search.keywords)}\n")

        es = ElasticSearchManager(page=from_, size=input.size,
                                  index=index, **els_config)
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
        data_type = make_query(
            "match", "conts_dataset_reg_yn", {"operator": "OR", "query": "Y"}
        )
        es.body["query"]["bool"]["filter"].append(data_type)

        sort_list = [{item.field: item.order} for item in input.sortOption]
        es.set_sort(sort_list)
        search_data = es.search(input.resultField)

        # assets index count y
        body = deepcopy(es.body)
        del body["sort"]
        data_dict["C"] = es.conn.count(index="kt_biz_asset", body=body)["count"]

        # assets index assets n = n+y
        body["query"]["bool"]["filter"] = body["query"]["bool"]["filter"][:-1]
        data_dict["A"] = es.conn.count(index="kt_biz_asset", body=body)["count"]

        # meta index count
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
