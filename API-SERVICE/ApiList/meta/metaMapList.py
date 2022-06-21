from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_token_info, make_res_msg
from fastapi.logger import logger
from starlette.requests import Request


def api(request: Request) -> Dict:
    user_info = get_token_info(request.headers)

    meta_map_query = """
    select
        tbmn.kor_nm,
        tbmn.eng_nm,
        tbmm.item_id,
        tbmm.nm_id
    from
        tb_biz_meta_name as tbmn
    join tb_biz_meta_map as tbmm
    on tbmm.nm_id = tbmn.nm_id;
    """

    try:
        db = connect_db(config.db_info)
        meta_map = db.select(meta_map_query)
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        result = make_res_msg(1, "",  meta_map[0],  meta_map[1])
    return result
