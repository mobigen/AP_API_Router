from fastapi.logger import logger
from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_token_info, make_res_msg
from Utils.DataBaseUtil import convert_data
from starlette.requests import Request


def api(datasetId: str, request: Request) -> Dict:
    user_info = get_token_info(request.headers)

    query = f'''select T."BIZ_DATASET_ID" as "rowId",
                array_agg(T."KOR_NM") as "KOR_NM",
                array_agg(T."ENG_NM") as "ENG_NM",
                array_agg(T."TYPE")     as "TYPE",
                array_agg(T."ITEM_VAL") as "ITEM_VAL",
                array_agg(T."ITEM_ID")  as "ITEM_ID"
            from (select 
                        "BIZ_DATASET_ID",
                        tbm."ITEM_ID",
                        tbm."ITEM_VAL",
                        tbmm."NM_ID",
                        tbmn."KOR_NM",
                        tbmn."ENG_NM",
                        tbmn."TYPE"
                    from tb_biz_meta tbm
                        right join tb_biz_meta_map tbmm on tbm."ITEM_ID" = tbmm."ITEM_ID"
                        left join tb_biz_meta_name tbmn on tbmm."NM_ID" = tbmn."NM_ID"
                    where "BIZ_DATASET_ID" = {convert_data(datasetId)}
                    order by "BIZ_DATASET_ID", "ITEM_ID") T
            group by "BIZ_DATASET_ID"
            order by "BIZ_DATASET_ID";'''

    v_meta_name_query = "SELECT * FROM v_biz_meta;"

    try:
        db = connect_db(config.db_type, config.db_info)
        biz_meta_detail = db.select(query)
        v_meta_name = db.select(v_meta_name_query)
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        result = make_res_msg(1, "", biz_meta_detail[0], v_meta_name[0])
    return result
