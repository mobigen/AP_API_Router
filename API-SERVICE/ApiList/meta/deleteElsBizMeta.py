from Utils.CommonUtil import get_exception_info
from ELKSearch.Manager.manager import ElasticSearchManager


def api(biz_dataset_id: str):
    try:
        es = ElasticSearchManager()
        es.delete("biz_dataset_id", biz_dataset_id)

    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = {"result": 1, "errorMessage": ""}
    return result

