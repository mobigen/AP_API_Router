from typing import Dict
from copy import deepcopy
from Utils.ESUtils import div_keyword, make_query
from Utils.CommonUtil import get_exception_info
from ConnectManager.ElasticSearchManager import ESSearch


def api(perPage: int = 12,
        curPage: int = 1,
        keywordList: list = [],
        sortOption: list = [],
        filterOption: dict = dict(),
        dataSrttn: str = "전체",
        matchOption: str = "AND") -> Dict:

    data_srttn = {
        # search_keyword: (result_key, result_data)
        "전체": "totalCount",
        "보유데이터": "hasCount",
        "연동데이터": "innerCount",
        "외부데이터": "externalCount",
        "해외데이터": "overseaCount"
    }
    data = dict()

    try:
        keyword_dict = div_keyword(keywordList)
        es = ESSearch(cur_from=curPage,size=perPage)
        es.set_sort(sortOption)

        if len(filterOption):
            es.set_filter(filterOption)

        es.set_match(keyword_dict,matchOption)

        for ko_nm, eng_nm in data_srttn.items():
            cnt_body_query = {"query": deepcopy(es.body["query"])}

            if "filter" not in cnt_body_query["query"]["bool"].keys():
                cnt_body_query["query"]["bool"]["filter"] = []

            if ko_nm != "전체":
                filter_srttn = make_query("match","data_srttn",ko_nm)
                cnt_body_query["query"]["bool"]["filter"].append(filter_srttn)

            cnt = es.conn.count(index=es.index,body=cnt_body_query)["count"]
            data[eng_nm] = cnt

        if dataSrttn != "전체":
            filter_srttn = make_query("match","data_srttn",dataSrttn)
            es.body["query"]["bool"]["filter"].append(filter_srttn)

        biz_meta_elk = es.search()
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        search_list = [data["_source"] for data in biz_meta_elk["hits"]["hits"]]
        data["searchList"] = search_list
        result = {"result": 1, "errorMessage": "", "data": data}

    return result
