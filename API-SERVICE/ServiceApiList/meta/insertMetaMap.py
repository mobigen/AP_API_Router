import uuid
from typing import Dict
from pydantic import BaseModel
from ServiceUtils.CommonUtil import connect_db, get_exception_info, convert_data


class NmIdList(BaseModel):
    nm_id_list: list


def api(insert: NmIdList) -> Dict:
    view_col = ["biz_dataset_id"]
    drop_view_wrap_query = "DROP VIEW IF EXISTS v_biz_meta_wrap"
    drop_view_meta_query = "DROP VIEW IF EXISTS v_biz_meta"
    create_view_meta_query = "CREATE OR REPLACE VIEW v_biz_meta \
                                AS SELECT tbmm.nm_id AS nm_id, \
                                          tbmn.kor_nm AS kor_nm, \
                                          tbmn.eng_nm AS eng_nm, \
                                          tbmm.item_id as item_id \
                              FROM tb_biz_meta_map tbmm \
                                  INNER JOIN tb_biz_meta_name tbmn ON tbmm.nm_id = tbmn.nm_id;"
    delete_map_query = "DELETE FROM tb_biz_meta_map WHERE nm_id = {0}"
    map_insert_query = "INSERT INTO tb_biz_meta_map (item_id, nm_id) VALUES ({0}, {1});"
    meta_map_query = "SELECT * FROM tb_biz_meta_map"
    nm_id_query = "SELECT nm_id FROM tb_biz_meta_map"

    map_item_query = "SELECT DISTINCT \
                         meta_map.item_id,\
                         tbmn.eng_nm\
                     FROM\
                         tb_biz_meta_name tbmn\
                     LEFT JOIN tb_biz_meta_map meta_map ON\
                         tbmn.nm_id = meta_map.nm_id\
                     WHERE item_id IS NOT NULL"

    ddl_dataset_id = "CREATE VIEW v_biz_meta_wrap AS\
                          SELECT\
                              {0}\
                          FROM tb_biz_meta\
                          GROUP BY biz_dataset_id"
    try:
        db = connect_db()

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
        col_format = "\t\tMAX(CASE WHEN item_id = {0} THEN item_val END) AS {1}"
        view_col = view_col + [col_format.format(convert_data(meta_map["item_id"]), meta_map["eng_nm"])
                               for meta_map in meta_map_item]

        db.execute(ddl_dataset_id.format(",\n".join(view_col)))
        db.execute(create_view_meta_query)

        # return data
        meta_map_list = db.select(meta_map_query)[0]

    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = meta_map_list
    return result
