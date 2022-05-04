import uuid
from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db
from Utils.DataBaseUtil import convert_data


def api() -> Dict:
    db = connect_db(config.db_type, config.db_info)
    query = "SELECT biz_dataset_id FROM tb_biz_meta;"
    biz_meta_list = db.select(query)[0]

    for biz_meta in biz_meta_list:        
        query = f'UPDATE tb_biz_meta\
                  SET biz_dataset_id = ({convert_data(uuid.uuid4())})\
                  WHERE biz_dataset_id = {convert_data(biz_meta["biz_dataset_id"])};'
        db.execute(query)
    
    query = "SELECT item_id as itemId, item_val as itemVal FROM tb_biz_meta;"
    biz_meta_list = db.select(query)[0]
    
    return biz_meta_list

