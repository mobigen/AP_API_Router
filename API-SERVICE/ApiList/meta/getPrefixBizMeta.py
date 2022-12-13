from typing import Dict, Optional
from pydantic import BaseModel
from ELKSearch.Manager.manager import ElasticSearchManager
from Utils.CommonUtil import get_exception_info
from ELKSearch.Utils.database_utils import get_config
from ApiService.ApiServiceConfig import config


class Prefix(BaseModel):
    size: int
    keyword: str
    index: Optional[str] = ""
    field: Optional[str] = ""


def api(input: Prefix) -> Dict:
    """
    Auto Complete data_nm
    DB의 Like 검색과 유사함
    :param keyword: type dict, ex) {"data_name" : "테"}
    :return:
    """
    if input.field == "":
        input.field = "data_nm"
    query = {input.field: input.keyword}
    els_config = get_config(config.root_path,"config.ini")[config.db_type[:-3]]
    try:
        if input.index != "":
            els_config["index"] = input.index
        es = ElasticSearchManager(**els_config)

        es.size = input.size
        prefix_data = es.prefix(query,[input.field])

    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        prefix_data = [data["_source"]["data_nm"] for data in prefix_data["hits"]["hits"]]
        result = {"result": 1, "errorMessage": "", "data": prefix_data}

    return result
