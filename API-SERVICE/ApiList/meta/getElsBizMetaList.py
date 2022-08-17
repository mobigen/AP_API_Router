from typing import Dict
from Utils.CommonUtil import get_exception_info
from Utils.ESUtils import ESSearch


def api(perPage: int = 12,
        curPage: int = 1,
        keyword1: str = "",
        keyword2: str = "",
        keyword3: str = "",
        sort_field: str = "_score") -> Dict:
    try:
        es = ESSearch(cur_from=curPage,size=perPage)
        es.div_keyword([keyword1,keyword2,keyword3])
        es.set_match()
        biz_meta_elk = es.conn.search(index=es.index,body=es.body)

    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        search_list = [data["_source"] for data in biz_meta_elk["hits"]["hits"]]
        data = {"totalcount": biz_meta_elk["hits"]["total"]["value"],
                "searchList": search_list}
        result = {"result": 1, "errorMessage": "", "data": data}

    return result
