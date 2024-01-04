import logging
from datetime import datetime, timedelta

from batch_service.app.common.config import settings, base_dir
from batch_service.app.common.const import BizDataTable, CkanDataTable
from batch_service.app.common.utils import default_search_set, data_process, index_set
from batch_service.app.database.conn import db

logger = logging.getLogger()


# els update condition
def time_check_cond(query, table_nm, date, op=""):
    return query["where_info"].append({
        "table_nm": table_nm,
        "key": "modified_dt",
        "value": date,
        "compare_op": "=",
        "op": op,
    })


def insert_meta(retv_update=False):
    index_nm = "biz_meta"
    els_host = settings.ELS_INFO.ELS_HOST
    els_port = settings.ELS_INFO.ELS_PORT
    try:
        if not retv_update:
            index = index_set(host=els_host, port=els_port)
            index.delete(index_nm)
            index.create(index_nm, path=f"{base_dir}/resources/mapping")

        docmanager = default_search_set(host=els_host, port=els_port, index=index_nm)

        with db.get_db_manager() as session:
            query = BizDataTable.get_select_query("D")
            if retv_update:
                today = datetime.today().strftime("%Y-%m-%d %H:%M:00")
                query = time_check_cond(query, BizDataTable.table_nm, today, "and")
            meta_list = session.query(**query).all()[0]

        logger.info(len(meta_list))

        for meta in meta_list:
            insert_body = data_process(meta)
            docmanager.set_body(insert_body["_source"])
            res = docmanager.insert(insert_body["_id"])
            logger.info(res)
    except Exception as e:
        print(e)


def insert_ckan(retv_update=False):
    index_nm = "v_biz_meta_oversea_els"
    els_host = settings.ELS_INFO.ELS_HOST
    els_port = settings.ELS_INFO.ELS_PORT
    try:
        if not retv_update:
            index = index_set(host=els_host, port=els_port)
            index.delete(index_nm)
            index.create(index_nm, path=f"{base_dir}/resources/mapping")

        docmanager = default_search_set(host=els_host, port=els_port, index=index_nm)

        with db.get_db_manager() as session:
            query = CkanDataTable.get_select_query("")
            if retv_update:
                today = datetime.today().strftime("%Y-%m-%d %H:%M:00")
                query = time_check_cond(query, CkanDataTable.table_nm, today, "and")
                query["where_info"] = query["where_info"][1:]
            else:
                query.pop("where_info")
            oversea_list = session.query(**query).all()[0]
        logger.info(oversea_list)
        logger.info(len(oversea_list))

        for oversea in oversea_list:
            insert_body = data_process(oversea)
            docmanager.set_body(insert_body["_source"])
            res = docmanager.insert(insert_body["_id"])
            logger.info(res)
    except Exception as e:
        print(e)
