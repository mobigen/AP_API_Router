import re
from typing import Dict
from Utils.CommonUtil import get_exception_info, connect_db, convert_data
from ELKSearch.Manager.manager import ElasticSearchManager
from ELKSearch.Utils.database_utils import get_config
from ELKSearch.Utils.elasticsearch_utils import data_process
from ApiService.ApiServiceConfig import config


def api(biz_dataset_id: str) -> Dict:
    els_dict = dict()
    els_config = get_config(config.root_path,"config.ini")[config.db_type[:-3]]
    query = f"SELECT * FROM v_biz_meta_info WHERE biz_dataset_id = {convert_data(biz_dataset_id)}"
    try:
        db = connect_db()
        es = ElasticSearchManager(**els_config)
        biz_data = db.select(query)[0][0]

        els_dict = data_process(biz_data)
        es.insert(els_dict,biz_dataset_id)
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = {"result": 1, "errorMessage": ""}
    return result
