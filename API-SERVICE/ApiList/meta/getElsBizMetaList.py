from typing import Dict
from ELKSearch.Manager.manager import ElasticSearchManager
from ELKSearch.Utils.model import InputModel
from ELKSearch.Utils.elasticsearch_utils import make_query, base_search_query
from Utils.CommonUtil import get_exception_info


def api(input: InputModel) -> Dict:
    data_srttn = {
        # search_keyword: (result_key, result_data)
        "보유데이터": "hasCount",
        "연동데이터": "innerCount",
        "외부데이터": "externalCount",
        "해외데이터": "overseaCount",
        "전체": "totalCount"
    }
    data_dict = dict()
    from_ = input.from_ - 1

    try:
        es = ElasticSearchManager(page=from_, size=input.size)
        es.set_sort(input.sortOption)

        ############ search option ############
        action = "query"
        sub_action = "must"
        query_dict = base_search_query(action,sub_action,input.searchOption)

        # ############ filter option ############
        sub_action = "filter"
        item_dict = base_search_query(action,sub_action,input.filterOption)
        query_dict.update(item_dict)
        search_query = make_query(action,"bool", query_dict)
        es.body.update(search_query)

        # ############ sort option ############
        sort_list = [{item.field: item.order} for item in input.sortOption]
        es.set_sort(sort_list)
        search_data = es.search(input.resultField)

        # ############ data_srttn ############
        i = None
        for j,item in enumerate(item_dict["filter"]):
            if "data_srttn" in item["match"].keys():
                i = j
                break
            else:
                i = None

        for ko_nm, eng_nm in data_srttn.items():
            if i is None:
                cnt_query = make_query("match","data_srttn",{'operator': 'OR', 'query': ko_nm})
                item_dict["filter"].append(cnt_query)
                i = -1
            else:
                item_dict["filter"][i]["match"]["data_srttn"]["query"] = ko_nm

            if ko_nm == "전체":
                del item_dict["filter"][i]

            query_dict.update(item_dict)
            cnt_query = make_query("query","bool",query_dict)
            cnt = es.conn.count(index=es.index,body=cnt_query)["count"]
            data_dict[eng_nm] = cnt

    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        search_list = [data["_source"] for data in search_data["hits"]["hits"]]
        data_dict["searchList"] = search_list
        result = {"result": 1, "errorMessage": "", "data": data_dict}

    return result
