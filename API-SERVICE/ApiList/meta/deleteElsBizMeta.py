from Utils.CommonUtil import get_exception_info
from ELKSearch.Manager.manager import ElasticSearchManager
from ApiService.ApiServiceConfig import config
from ELKSearch.Utils.database_utils import get_config


def api(biz_dataset_id: str):
    els_config = get_config(config.root_path,"config.ini")[config.db_type[:-3]]
    try:
        es = ElasticSearchManager(**els_config)
        es.delete("biz_dataset_id", biz_dataset_id)

    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = {"result": 1, "errorMessage": ""}
    return result

