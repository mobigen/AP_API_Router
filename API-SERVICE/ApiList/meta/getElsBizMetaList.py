from typing import Dict, Optional
from copy import deepcopy
from pydantic import BaseModel
from Utils.ESUtils import div_keyword, make_query
from Utils.CommonUtil import get_exception_info
from ConnectManager.ElasticSearchManager import ESSearch


class SearchOption(BaseModel):
    perPage: int = 12
    curPage: int = 1
    keywordList: Optional[list] = None
    sortOption: Optional[list] = []
    filterOption: dict = dict()
    dataSrttn: str = "전체"
    filterOperator: str = "OR"
    matchOption: str = "AND"


def api(search_option: SearchOption) -> Dict:

    data_srttn = {
        # search_keyword: (result_key, result_data)
        "전체": "totalCount",
        "보유데이터": "hasCount",
        "연동데이터": "innerCount",
        "외부데이터": "externalCount",
        "해외데이터": "overseaCount"
    }
    data = dict()
    search_option.curPage = search_option.curPage - 1
    from_page = search_option.curPage * search_option.perPage
    try:
        # 숫자랑 특수문자 조회
        keyword_dict = div_keyword(search_option.keywordList)
        es = ESSearch(cur_from=from_page,size=search_option.perPage)
        es.set_sort(search_option.sortOption)

        if any(search_option.filterOption.values()):
            es.set_filter(search_option.filterOption,search_option.filterOperator)

        es.set_match(keyword_dict,search_option.matchOption)

        for ko_nm, eng_nm in data_srttn.items():
            cnt_body_query = {"query": deepcopy(es.body["query"])}

            if "filter" not in cnt_body_query["query"]["bool"].keys():
                cnt_body_query["query"]["bool"]["filter"] = []

            if ko_nm != "전체":
                filter_srttn = make_query("match","data_srttn",ko_nm)
                cnt_body_query["query"]["bool"]["filter"].append(filter_srttn)

            cnt = es.conn.count(index=es.index,body=cnt_body_query)["count"]
            data[eng_nm] = cnt

        if search_option.dataSrttn != "전체":
            filter_srttn = make_query("match","data_srttn",search_option.dataSrttn)

            if "filter" not in es.body["query"]["bool"].keys():
                es.body["query"]["bool"]["filter"] = []

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
