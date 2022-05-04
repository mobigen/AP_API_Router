from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db
from Utils.DataBaseUtil import convert_data


def api() -> Dict:
    db = connect_db(config.db_type, config.db_info)
    meta_name_query = """
            select T.biz_dataset_id      as rowId,
               array_agg(T.item_val) as data,
               array_agg(T.item_id)  as columnKey
        from (select biz_dataset_id, tbm.item_id, tbm.item_val, tbmm.name_id, kor_name, eng_name
              from metasch.tb_biz_meta tbm
                       right join metasch.tb_biz_meta_map tbmm on tbm.item_id = tbmm.item_id
                       left join metasch.tb_biz_meta_name tbmn on tbmm.name_id = tbmn.name_id
              order by biz_dataset_id, item_id) T
        group by biz_dataset_id
        order by biz_dataset_id;
    """
    bizmeta_list = db.select(meta_name_query)
    
    v_meta_map_query = "SELECT kor_name,eng_name,name_id FROM tb_biz_meta_name;"
    v_meta_map = db.select(v_meta_map_query)

    return {"result" : "", "errorMessage" : "", "data": {"body": bizmeta_list[0],"header":v_meta_map[0]}}