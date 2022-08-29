from typing import Dict
from Utils.ESUtils import div_keyword, make_query, get_srttn_count
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
        "전체": ["totalCount", None],
        "보유데이터": ["hasCount", None],
        "연동데이터": ["innerCount", None],
        "외부데이터": ["externalCount", None],
        "해외데이터": ["overseaCount", None]
    }

    try:
        keyword_dict = div_keyword(keywordList)
        es = ESSearch(cur_from=curPage,size=perPage)
        es.set_sort(sortOption)

        if len(filterOption):
            es.set_filter(filterOption)

        if len(dataSrttn) and dataSrttn != "전체":
            count_name = data_srttn[dataSrttn][0]
            filter_srttn = make_query("match","data_srttn",dataSrttn)
            es.body["query"]["bool"]["filter"].append(filter_srttn)
            data_srttn.pop(dataSrttn)
        else:
            count_name = "totalCount"

        es.set_match(keyword_dict,matchOption)
        biz_meta_elk = es.search()

        data = get_srttn_count(data_srttn,es)

    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        search_list = [data["_source"] for data in biz_meta_elk["hits"]["hits"]]
        data[count_name] = biz_meta_elk["hits"]["total"]["value"]
        data["searchList"] = search_list
        result = {"result": 1, "errorMessage": "", "data": data}

    return result
