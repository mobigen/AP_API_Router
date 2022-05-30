from fastapi.logger import logger
from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_token_info
from Utils.DataBaseUtil import convert_data
from starlette.requests import Request


def api(map_list: list ,request: Request) -> Dict:
    user_info = get_token_info(request.headers)

    view_col = ['"BIZ_DATASET_ID"']
    drop_view_query = "DROP VIEW v_biz_meta_wrap"
    truncate_query = "TRUNCATE tb_biz_meta_map;"
    map_insert_query = 'INSERT INTO tb_biz_meta_map ("ITEM_ID", "NM_ID") VALUES ({0}, {1});'
    meta_map_query = "SELECT * FROM tb_biz_meta_map"
    map_item_query = """
        select distinct 
            cast(meta_map."ITEM_ID" as INT) as ITEM_ID,
            tbmn."ENG_NM"
        from
            tb_biz_meta_name tbmn
        left join tb_biz_meta_map meta_map on
            tbmn."NM_ID" = meta_map."NM_ID"
        order by ITEM_ID asc
    """

    try:
        db = connect_db(config.db_type, config.db_info)
        db.execute(drop_view_query)
        db.execute(truncate_query)

        for meta_map in map_list:
            logger.info(meta_map)
            db.execute(map_insert_query.format(convert_data(meta_map["itemId"]),
                                               convert_data(meta_map["nameId"])))

        # create view v_biz_meta_wrap
        meta_map_item = db.select(map_item_query)[0]
        for i,meta_map in enumerate(meta_map_item):
            eng_name = meta_map["ENG_NM"]
            col_format = f'\t\tmax(case when "ITEM_ID" = {convert_data(i + 1)} then "ITEM_VAL" end) as {eng_name}'
            view_col.append(col_format)

        view_col = ',\n'.join(view_col)
        ddl_dataset_id = f"""
            create view v_biz_meta_wrap as
            select
                {view_col}
            from tb_biz_meta
            group by "BIZ_DATASET_ID"
        """
        db.execute(ddl_dataset_id)

        # return data
        meta_map_list = db.select(meta_map_query)[0]
    # 수정 해야함
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        result = meta_map_list
    return result
