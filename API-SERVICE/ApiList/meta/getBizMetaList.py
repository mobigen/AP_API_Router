from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db
from fastapi.logger import logger


def api() -> Dict:
    meta_name_query = """
            select T.biz_dataset_id      as rowId,
               array_agg(T.item_val) as data,
               array_agg(T.item_id)  as columnKey
        from (select biz_dataset_id, tbm.item_id, tbm.item_val, tbmm.name_id, kor_name, eng_name
              from meta.tb_biz_meta tbm
                       right join meta.tb_biz_meta_map tbmm on tbm.item_id = tbmm.item_id
                       left join meta.tb_biz_meta_name tbmn on tbmm.name_id = tbmn.name_id
              order by biz_dataset_id, item_id) T
        group by biz_dataset_id
        order by biz_dataset_id;
    """
    v_meta_name_query = "SELECT * FROM v_biz_meta_name;"

    try:
        db = connect_db(config.db_type, config.db_info)
        bizmeta_list = db.select(meta_name_query)
        v_meta_name = db.select(v_meta_name_query)
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        result = {"result": 1, "errorMessage": "", "data": {
            "body": bizmeta_list[0], "header": v_meta_name[0]}}
    return result
