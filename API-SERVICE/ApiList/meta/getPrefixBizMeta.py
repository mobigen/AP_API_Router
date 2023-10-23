from typing import Dict
from fastapi.logger import logger
from pydantic import BaseModel
from ELKSearch.Manager.manager import ElasticSearchManager
from Utils.CommonUtil import get_exception_info
from ELKSearch.Utils.database_utils import get_config
from ApiService.ApiServiceConfig import config


class Prefix(BaseModel):
    index: str
    size: int
    fields: list
    query: str


def api(input: Prefix) -> Dict:
    """
    Auto Complete data_nm
    DB의 Like 검색과 유사함
    :param keyword: type dict, ex) {"data_name" : "테"}
    :return:
    """
    if not len(input.fields):
        input.fields = ["data_nm"]
    els_config = get_config(config.root_path,"config.ini")[config.db_type[:-3]]
    try:
        els_config["index"] = ["biz_meta","v_biz_meta_oversea_els"]
        es = ElasticSearchManager(**els_config)
        es.size = input.size
        input.query = f"(*{input.query}*)"
        del input.index
        del input.size
        search_query = {"query_string": input.dict()}
        logger.info(search_query)

        body = {
            "query": {
                "bool": {
                    "must": [search_query]
                }
            }
        }
        es.body = body
        logger.info(es.body)
        prefix_data = es.search(input.fields)
        logger.info(prefix_data)

        if not len(prefix_data):
            return {"result": 1,"data": []}
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        prefix_data = [data["_source"]["data_nm"] for data in prefix_data["hits"]["hits"]]
        result = {"result": 1, "errorMessage": "", "data": prefix_data}

    return result
