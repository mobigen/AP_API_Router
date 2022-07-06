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

    view_col = ['biz_dataset_id']
    drop_view_wrap_query = "DROP VIEW IF EXISTS v_biz_meta_wrap"
    drop_view_meta_query = "DROP VIEW IF EXISTS v_biz_meta"
    create_view_meta_query = "CREATE OR REPLACE VIEW v_biz_meta \
                                AS SELECT tbmm.nm_id AS nm_id, \
                                          tbmn.kor_nm AS kor_nm, \
                                          tbmn.eng_nm AS eng_nm, \
                                          tbmm.item_id as item_id \
                              FROM tb_biz_meta_map tbmm \
                                  INNER JOIN tb_biz_meta_name tbmn ON tbmm.nm_id = tbmn.nm_id;"
    delete_map_query = 'DELETE FROM tb_biz_meta_map WHERE nm_id = {0}'
    map_insert_query = 'INSERT INTO tb_biz_meta_map (item_id, nm_id) VALUES ({0}, {1});'
    meta_map_query = "SELECT * FROM tb_biz_meta_map"
    nm_id_query = 'SELECT nm_id FROM tb_biz_meta_map'

    map_item_query = "SELECT distinct \
                         meta_map.item_id,\
                         tbmn.eng_nm\
                     FROM\
                         tb_biz_meta_name tbmn\
                     LEFT JOIN tb_biz_meta_map meta_map ON\
                         tbmn.nm_id = meta_map.nm_id\
                     WHERE item_id IS NOT NULL"

    try:
        db = connect_db(config.db_info)

        nm_id_set = {_["nm_id"] for _ in db.select(nm_id_query)[0]}
        req_nm_ids = set(insert.nm_id_list)
        delete_nm_ids = nm_id_set - req_nm_ids
        nm_id_set = req_nm_ids - nm_id_set

        for nm_id in delete_nm_ids:
            db.execute(delete_map_query.format(convert_data(nm_id)))

        for nm_id in nm_id_set:
            db.execute(map_insert_query.format(convert_data(uuid.uuid4()),
                                               convert_data(nm_id)))

        # drop view v_biz_meta_wrap
        db.execute(drop_view_wrap_query)
        db.execute(drop_view_meta_query)

        # create view v_biz_meta_wrap
        meta_map_item = db.select(map_item_query)[0]
        for i, meta_map in enumerate(meta_map_item):
            col_format = f'\t\tmax(case when item_id = {convert_data(meta_map["item_id"])} ' \
                         f'then item_val end) as {meta_map["eng_nm"]}'
            view_col.append(col_format)

        view_col = ',\n'.join(view_col)
        ddl_dataset_id = f"CREATE VIEW v_biz_meta_wrap AS\
                          SELECT\
                              {view_col}\
                          FROM tb_biz_meta\
                          GROUP BY biz_dataset_id"
        db.execute(ddl_dataset_id)
        db.execute(create_view_meta_query)

        # return data
        meta_map_list = db.select(meta_map_query)[0]

    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        result = meta_map_list
    return result
