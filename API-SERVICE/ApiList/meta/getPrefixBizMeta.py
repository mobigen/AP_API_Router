from typing import Dict
from ELKSearch.Manager.manager import ElasticSearchManager
from Utils.CommonUtil import get_exception_info
from ELKSearch.Utils.database_utils import get_config
from ApiService.ApiServiceConfig import config


def api(size: int, keyword: str) -> Dict:
    """
    Auto Complete data_nm
    DB의 Like 검색과 유사함
    :param keyword: type dict, ex) {"data_name" : "테"}
    :return:
    """
    field = "data_nm"
    query = {field: keyword}
    els_config = get_config(config.root_path,"config.ini")["katech"]
    try:
        es = ElasticSearchManager(**els_config)
        es.size = size
        prefix_data = es.prefix(query,[field])

    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        prefix_data = [data["_source"]["data_nm"] for data in prefix_data["hits"]["hits"]]
        result = {"result": 1, "errorMessage": "", "data": prefix_data}

    return result
