from dataclasses import replace
import re
from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db
from Utils.DataBaseUtil import convert_data

def api(data_set_id:str) -> Dict:
    db = connect_db(config.db_type, config.db_info)
    query = f'select T.biz_dataset_id as rowId,\
                array_agg(T.kor_name) as kor_name,\
                array_agg(T.eng_name) as eng_name,\
                array_agg(T.type)     as type,\
                array_agg(T.item_val) as data,\
                array_agg(T.item_id)  as columnKey\
            from (select biz_dataset_id, tbm.item_id, tbm.item_val, tbmm.name_id, kor_name, eng_name, type\
                    from tb_biz_meta tbm\
                        right join tb_biz_meta_map tbmm on tbm.item_id = tbmm.item_id\
                        left join tb_biz_meta_name tbmn on tbmm.name_id = tbmn.name_id\
                    where biz_dataset_id = {convert_data(data_set_id)}\
                    order by biz_dataset_id, item_id) T\
            group by biz_dataset_id\
            order by biz_dataset_id;'
    biz_meta_detail = db.select(query)
    
    v_meta_name_query = "SELECT * FROM v_biz_meta_name;"
    v_meta_name = db.select(v_meta_name_query)

    return {"result" : "", "errorMessage" : "", "data": {"body": biz_meta_detail[0],"header":v_meta_name[0]}}