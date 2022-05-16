from fastapi.logger import logger
from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db
from Utils.DataBaseUtil import convert_data


def api() -> Dict:
    view_col = ["biz_dataset_id"]
    drop_view_query = "DROP VIEW v_biz_meta_wrap"
    truncate_query = "TRUNCATE tb_biz_meta_map;"
    meta_name_query = "SELECT name_id FROM tb_biz_meta_name;"
    meta_map_query = "SELECT * FROM tb_biz_meta_map"
    map_item_query = """
        select distinct 
            cast(meta_map.item_id as INT) as item_id,
            tbmn.eng_name as eng_name
        from
            tb_biz_meta_name tbmn
        left join tb_biz_meta_map meta_map on
            tbmn.name_id = meta_map.name_id
        order by item_id asc
    """

    try:
        db = connect_db(config.db_type, config.db_info)
        db.execute(drop_view_query)
        db.execute(truncate_query)
        meta_name_list = db.select(meta_name_query)[0]

        # insert meta map
        for i, meta_name in enumerate(meta_name_list):
            query = f'INSERT INTO tb_biz_meta_map (item_id,name_id)\
                        VALUES ({convert_data(i + 1)},{convert_data(meta_name["name_id"])});'
            db.execute(query)

        # create view v_biz_meta_wrap
        meta_map_item = db.select(map_item_query)[0]
        for i,meta_map in enumerate(meta_map_item):
            eng_name = meta_map["eng_name"]
            col_format = f"\t\tmax(case when item_id = {convert_data(i + 1)} then item_val end) as {eng_name}"
            view_col.append(col_format)

        view_col = ',\n'.join(view_col)
        ddl_dataset_id = f"""
            create view v_biz_meta_wrap as
            select
                {view_col}
            from tb_biz_meta
            group by biz_dataset_id
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
