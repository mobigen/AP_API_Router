from typing import Dict
from datetime import datetime
from ELKSearch.Manager.manager import ElasticSearchManager
from ELKSearch.Utils.model import InputModel
from ELKSearch.Utils.elasticsearch_utils import make_query, base_search_query
from ELKSearch.Utils.database_utils import get_config
from Utils.CommonUtil import get_exception_info
from ApiService.ApiServiceConfig import config


def extra_filter(option_list):
    els_katech_option = ["ctgry","data_shap","data_prv_desk"]
    for item in option_list:
        for col in els_katech_option:
            if col in item.field:
                item.field.append(f"re_{col}")
                index = item.field.index(col)
                del item.field[index]
                item.keywords = [v.replace(" ","") for v in item.keywords]

        tmp = []
        for field in item.field:
            if item.field in ["data_nm", "data_desc"]:
                col = field + ".korean_analyzer"
            else:
                col = field
            tmp.append(col)
        item.field = tmp

    return option_list


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
    els_config = get_config(config.root_path,"config.ini")[config.db_type[:-3]]

    try:
        if input.chk and len(input.searchOption):
            with open(f"{config.root_path}/log/{config.category}/{datetime.today().strftime('%Y%m%d')}_search.log","a") as fp:
                for search in input.searchOption:
                    fp.write(f"{str(search.keywords)}\n")

        es = ElasticSearchManager(page=from_, size=input.size, **els_config)
        es.set_sort(input.sortOption)

        ############ search option ############
        action = "query"
        sub_action = "must"
        input.searchOption = extra_filter(input.searchOption)
        query_dict = base_search_query(action,sub_action,input.searchOption)

        # ############ filter option ############
        sub_action = "filter"
        input.filterOption = extra_filter(input.filterOption)
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
