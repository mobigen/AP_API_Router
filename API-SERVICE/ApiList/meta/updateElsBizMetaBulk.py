from typing import Dict
from elasticsearch import helpers
from Utils.CommonUtil import get_exception_info, connect_db
from ELKSearch.Manager.manager import ElasticSearchManager
from ELKSearch.Utils.database_utils import get_config
from ELKSearch.Utils.elasticsearch_utils import data_process
from ApiService.ApiServiceConfig import config


def api() -> Dict:
    """
    bulk로 업데이트 할 때 timeout이 발생하는 이슈가 있음
    """
    els_config = get_config(config.root_path,"config.ini")[config.db_type[:-3]]
    # bulk_meta_item = list()
    db_query = f"SELECT * FROM v_biz_meta_info  WHERE status = 'D'"

    try:
        db = connect_db()
        es = ElasticSearchManager(**els_config)

        meta_wrap_list = db.select(db_query)[0]
        for meta_wrap in meta_wrap_list:
            els_dict = data_process(meta_wrap)
            es.insert(els_dict["_source"],meta_wrap["biz_dataset_id"])
            # bulk_meta_item.append(els_dict)
        # helpers.bulk(es.conn, bulk_meta_item, index=es.index)

    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = {"result": 1, "errorMessage": ""}
    return result
