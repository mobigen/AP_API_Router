from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_token_info, make_res_msg
from fastapi.logger import logger
from starlette.requests import Request


def api(perPage: int, curPage: int, request: Request) -> Dict:
    user_info = get_token_info(request.headers)

    curPage = curPage - 1
    meta_name_query = f"""
        select
            p.*
        from tb_biz_meta_name as p
        join (
            SELECT kor_nm,
                   eng_nm,
                   show_odrg,
                   nm_id,
                   (case
                       when type = 0 then 'text'
                       when type = 1 then 'int'
                       when type = 2 then 'binary'
                       end
                    ) as type,
                    ROW_NUMBER () OVER (ORDER BY nm_id DESC) as rowNo
            FROM tb_biz_meta_name
            order by nm_id
            limit {perPage}
            offset ({perPage} * {curPage})
        ) as t on p.nm_id = t.nm_id
    """
    total_cnt_query = "SELECT count(*) as totalCount FROM tb_biz_meta_name"

    try:
        db = connect_db(config.db_info)
        meta_name = db.select(meta_name_query)
        total_cnt = db.select(total_cnt_query)
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        result = make_res_msg(1, "", meta_name[0], meta_name[1])
        result["data"].update(total_cnt[0][0])
    return result
