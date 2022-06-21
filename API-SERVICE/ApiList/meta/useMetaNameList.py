from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_token_info, make_res_msg
from fastapi.logger import logger
from starlette.requests import Request


def api(request: Request) -> Dict:
    user_info = get_token_info(request.headers)

    meta_name_query = """        
        select                
            case
                when (select tbmm.nm_id from tb_biz_meta_map tbmm where tbmn.nm_id = tbmm.nm_id) is null then 0
                else 1
                end as use_meta,
            tbmn.kor_nm,
            tbmn.eng_nm,
            tbmn.show_odrg,
            case
                when tbmn.type = 0 then 'text'
                when tbmn.type = 1 then 'int'
                when tbmn.type = 2 then 'binary'
                end as type,
            tbmn.nm_id
        from tb_biz_meta_name tbmn
        order by tbmn.nm_id;"""

    try:
        db = connect_db(config.db_info)
        meta_name = db.select(meta_name_query)
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        result = make_res_msg(1, "", meta_name[0], meta_name[1])
    return result
