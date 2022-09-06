from Utils.CommonUtil import get_exception_info
from ConnectManager.ElasticSearchManager import ESSearch


def api(biz_dataset_id: str):
    try:
        es = ESSearch()
        es.delete("biz_dataset_id", biz_dataset_id)

    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = {"result": 1, "errorMessage": ""}
    return result

