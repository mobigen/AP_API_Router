from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_token_info, make_res_msg
from fastapi.logger import logger
from starlette.requests import Request


def api(request: Request) -> Dict:
    user_info = get_token_info(request.headers)

    meta_name_query = '''
            select T."BIZ_DATASET_ID" as rowId,
               array_agg(T."ITEM_VAL") as data,
               array_agg(T."ITEM_ID")  as columnKey
        from (select "BIZ_DATASET_ID", tbm."ITEM_ID", tbm."ITEM_VAL", tbmm."NM_ID", "KOR_NM", "ENG_NM"
              from tb_biz_meta tbm
                       left join tb_biz_meta_map tbmm on tbm."ITEM_ID" = tbmm."ITEM_ID"
                       left join tb_biz_meta_name tbmn on tbmm."NM_ID" = tbmn."NM_ID"
              order by "BIZ_DATASET_ID", "ITEM_ID") T
        group by "BIZ_DATASET_ID"
        order by "BIZ_DATASET_ID";
    '''
    v_meta_name_query = "SELECT * FROM v_biz_meta;"

    try:
        db = connect_db(config.db_type, config.db_info)
        bizmeta_list = db.select(meta_name_query)
        v_meta_name = db.select(v_meta_name_query)
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        result = make_res_msg(1, "", bizmeta_list[0], v_meta_name[0])
    return result
