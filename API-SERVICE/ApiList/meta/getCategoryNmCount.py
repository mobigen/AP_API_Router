from typing import Dict
from ELKSearch.Manager.manager import ElasticSearchManager
from ELKSearch.Utils.elasticsearch_utils import make_query
from Utils.CommonUtil import get_exception_info
from ELKSearch.Utils.database_utils import get_config
from ApiService.ApiServiceConfig import config


def api(nms) -> Dict:
    data_dict = {}
    key = "ctgry"
    els_config = get_config(config.root_path, "config.ini")[config.db_type[:-3]]
    try:
        ctgry_nm_list = nms.split(",")
        es = ElasticSearchManager(**els_config)
        for c_id in ctgry_nm_list:
            cnt_query = make_query("query", "match_phrase", {key: c_id})
            cnt = es.conn.count(index=es.index, body=cnt_query)["count"]
            data_dict[c_id.replace("+", "_")] = cnt

    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        pass
        result = {"result": 1, "errorMessage": "", "data": data_dict}

    return result
