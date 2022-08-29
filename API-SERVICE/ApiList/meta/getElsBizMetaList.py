from typing import Dict
from Utils.ESUtils import div_keyword
from Utils.CommonUtil import get_exception_info
from ConnectManager.ElasticSearchManager import ESSearch


def api(perPage: int = 12,
        curPage: int = 1,
        keywordList: list = [],
        sortOption: list = [],
        filterOption: dict = dict(),
        matchOption: str = "AND") -> Dict:
    try:
        keyword_dict = div_keyword(keywordList)
        es = ESSearch(cur_from=curPage,size=perPage)
        es.set_sort(sortOption)
        if len(filterOption):
            es.set_filter(filterOption)
        es.set_match(keyword_dict,matchOption)
        biz_meta_elk = es.search()

    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        search_list = [data["_source"] for data in biz_meta_elk["hits"]["hits"]]
        data = {"totalCount": biz_meta_elk["hits"]["total"]["value"],
                "searchList": search_list}
        result = {"result": 1, "errorMessage": "", "data": data}

    return result
