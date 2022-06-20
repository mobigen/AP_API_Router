import uuid
from typing import Dict
from pydantic import BaseModel
from fastapi.logger import logger
from starlette.requests import Request
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_token_info
from Utils.DataBaseUtil import convert_data


class NmIdList(BaseModel):
    nm_id_list: list


def api(insert: NmIdList, request: Request) -> Dict:
    user_info = get_token_info(request.headers)

    view_col = ['"BIZ_DATASET_ID" as biz_dataset_id']
    drop_view_query = "DROP VIEW IF EXISTS v_biz_meta_wrap"
    map_insert_query = 'INSERT INTO tb_biz_meta_map ("ITEM_ID", "NM_ID") VALUES ({0}, {1});'
    meta_map_query = "SELECT * FROM tb_biz_meta_map"
    nm_id_query = 'SELECT "NM_ID" FROM tb_biz_meta_map'

    map_item_query = """
        select distinct
            meta_map."ITEM_ID",
            tbmn."ENG_NM"
        from
            tb_biz_meta_name tbmn
        left join tb_biz_meta_map meta_map on
            tbmn."NM_ID" = meta_map."NM_ID"
        where "ITEM_ID" IS NOT NULL
    """

    try:
        db = connect_db(config.db_info)

        nm_id_set = {_["NM_ID"] for _ in db.select(nm_id_query)[0]}
        nm_id_set = set(insert.nm_id_list) - nm_id_set

        for nm_id in nm_id_set:
            db.execute(map_insert_query.format(convert_data(uuid.uuid4()),
                                               convert_data(nm_id)))

        # drop view v_biz_meta_wrap
        db.execute(drop_view_query)

        # create view v_biz_meta_wrap
        meta_map_item = db.select(map_item_query)[0]
        for i, meta_map in enumerate(meta_map_item):
            col_format = f'\t\tmax(case when "ITEM_ID" = {convert_data(meta_map["ITEM_ID"])} ' \
                         f'then "ITEM_VAL" end) as {meta_map["ENG_NM"]}'
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

    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        result = meta_map_list
    return result
