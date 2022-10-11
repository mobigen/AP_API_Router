from typing import Dict
from ELKSearch.Manager.manager import ElasticSearchManager
from ELKSearch.Utils.elasticsearch_utils import make_query
from Utils.CommonUtil import get_exception_info


def api(nms) -> Dict:
    data_dict = {}
    key = "ctgry"
    try:
        ctgry_nm_list = nms.split(",")
        es = ElasticSearchManager()
        for c_id in ctgry_nm_list:
            cnt_query = make_query("query","match_phrase",{key: c_id})
            cnt = es.conn.count(index=es.index, body=cnt_query)["count"]
            data_dict[c_id.replace("+","_")] = cnt

    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        pass
        result = {"result": 1, "errorMessage": "", "data": data_dict}

    return result
