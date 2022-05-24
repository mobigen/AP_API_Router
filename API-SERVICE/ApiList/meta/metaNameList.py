from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_token_info
from fastapi.logger import logger
from starlette.requests import Request


def api(perPage: int, curPage: int, request: Request) -> Dict:
    user_info = get_token_info(request.headers)

    curPage = curPage - 1
    meta_name_query = f"""
        select
            *
        from tb_biz_meta_name as p
        join (
            SELECT "KOR_NM",
                   "ENG_NM",
                   "SHOW_ODRG",
                   "NM_ID",
                   (case
                       when "TYPE" = 0 then 'text'
                       when "TYPE" = 1 then 'int'
                       when "TYPE" = 2 then 'binary'
                       end
                    ) as "TYPE",
                    ROW_NUMBER () OVER (ORDER BY "NM_ID" DESC) as rowNo
            FROM tb_biz_meta_name
            order by "NM_ID"
            limit {perPage}
            offset ({perPage} * {curPage})
        ) as t on p."NM_ID" = t."NM_ID"
    """
    total_cnt_query = "SELECT count(*) as totalCount FROM tb_biz_meta_name"
    v_meta_name_query = "SELECT * FROM v_biz_meta_name;"

    try:
        db = connect_db(config.db_type, config.db_info)
        meta_name = db.select(meta_name_query)
        total_cnt = db.select(total_cnt_query)
        v_meta_name = db.select(v_meta_name_query)
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        data = total_cnt[0][0]
        data.update({"body": meta_name[0], "header": v_meta_name[0]})
        result = {"result": "", "errorMessage": "", "data": data}
    return result
