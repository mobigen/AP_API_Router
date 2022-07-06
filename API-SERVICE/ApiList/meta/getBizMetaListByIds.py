from fastapi.logger import logger
from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, make_res_msg, get_exception_info
from Utils.DataBaseUtil import convert_data


def api(datasetIdList: str) -> Dict:
    v_meta_wrap_query = 'SELECT * FROM v_biz_meta_wrap WHERE biz_dataset_id in ({0})'

    try:
        db = connect_db(config.db_info)
        dataset_id_list = ','.join(
            [convert_data(biz_dataset_id) for biz_dataset_id in datasetIdList.split(",")]
        )
        meta_wrap = db.select(v_meta_wrap_query.format(dataset_id_list))
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = make_res_msg(1,"",meta_wrap[0],[])
        result["data"].pop("header")
        result["data"]["list"] = result["data"]["body"]
        del result["data"]["body"]
        logger.info(result)

    return result
