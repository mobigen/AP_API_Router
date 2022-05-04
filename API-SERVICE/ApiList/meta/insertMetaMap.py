from os import truncate
from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db
from Utils.DataBaseUtil import convert_data
    
    
def api() -> Dict:
    db = connect_db(config.db_type, config.db_info)
    
    truncate_query = "TRUNCATE tb_biz_meta_map;"
    db.execute(truncate_query)
    
    meta_name_query = "SELECT name_id FROM tb_biz_meta_name;"
    meta_name_list = db.select(meta_name_query)[0]
    
    for i,meta_name in enumerate(meta_name_list):
        query = f'INSERT INTO tb_biz_meta_map (item_id,name_id)\
                    VALUES ({convert_data(i + 1)},{convert_data(meta_name["name_id"])});'
        db.execute(query)    
    
    meta_map_query = "SELECT * FROM tb_biz_meta_map"
    meta_map_list = db.select(meta_map_query)[0]
    # 수정 해야함
    
    return meta_map_list