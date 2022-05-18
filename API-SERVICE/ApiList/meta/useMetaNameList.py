from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db
from fastapi.logger import logger


def api() -> Dict:
    meta_name_query = """        
        select                
            case
                when (select tbmm.NM_ID from tb_biz_meta_map tbmm where tbmn.NM_ID = tbmm.NM_ID) is null then 0
                else 1
                end as use_meta,
            tbmn.KOR_NM,
            tbmn.ENG_NM,
            tbmn.SHOW_ODRG,
            case
                when tbmn.TYPE = 0 then 'text'
                when tbmn.TYPE = 1 then 'int'
                when tbmn.TYPE = 2 then 'binary'
                end as type,
            tbmn.NM_ID
        from tb_biz_meta_name tbmn
        order by tbmn.NM_ID;"""

    try:
        db = connect_db(config.db_type, config.db_info)
        meta_name = db.select(meta_name_query)
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        result = {"result": 1, "errorMessage": "", "data": meta_name[0]}
    return result
