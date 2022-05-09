import uuid
from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db
from Utils.DataBaseUtil import convert_data


def api(biz_meta_list:list) -> Dict:
    db = connect_db(config.db_type, config.db_info)
    uid = uuid.uuid4()
    for biz_meta in biz_meta_list:        
        query = f'INSERT INTO tb_biz_meta (biz_dataset_id,item_id,item_val)\
                VALUES ({convert_data(uid)},{convert_data(biz_meta["itemId"])},{convert_data(biz_meta["itemVal"])});'
    
        db.execute(query)
    
    query = "SELECT item_id as itemId, item_val as itemVal FROM tb_biz_meta;"
    biz_meta_list = db.select(query)[0]
    
    return biz_meta_list

