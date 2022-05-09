from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db
from fastapi.logger import logger


def api() -> Dict:
    db = connect_db(config.db_type, config.db_info)
    meta_name_query = """        
        select                
            case
                when (select tbmm.name_id from tb_biz_meta_map tbmm where tbmn.name_id = tbmm.name_id) is null then 0
                else 1
                end as use_meta,
            tbmn.kor_name,
            tbmn.eng_name,
            tbmn.show_order,
            case
                when tbmn.type = 0 then 'text'
                when tbmn.type = 1 then 'int'
                when tbmn.type = 2 then 'binary'
                end as type,
            tbmn.name_id
        from tb_biz_meta_name tbmn
        order by tbmn.name_id;"""
    meta_name = db.select(meta_name_query)

    return {"result": "", "errorMessage": "", "data": meta_name[0]}
