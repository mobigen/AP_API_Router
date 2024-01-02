import logging

from batch_service.app.common.config import settings
from batch_service.app.common.const import BizDataTable, CkanDataTable
from batch_service.app.common.utils import default_search_set, data_process, default_process, index_set
from batch_service.app.database.conn import db

logger = logging.getLogger()


def insert_meta():
    index_nm = "biz_meta"
    els_host = settings.ELS_INFO.ELS_HOST
    els_port = settings.ELS_INFO.ELS_PORT
    try:
        index = index_set(host=els_host, port=els_port)
        index.delete(index_nm)
        index.create(index_nm)

        docmanager = default_search_set(host=els_host, port=els_port, index=index_nm)

        with db.get_db_manager() as session:
            query = BizDataTable.get_select_query("D")
            meta_list = session.query(**query).all()[0]

        logger.info(len(meta_list))

        for meta in meta_list:
            insert_body = data_process(meta)
            docmanager.set_body(insert_body)
            logger.info(docmanager.insert(insert_body["biz_dataset_id"]))
    except Exception as e:
        print(e)


def insert_ckan():
    index_nm = "v_biz_meta_oversea_els"
    els_host = settings.ELS_INFO.ELS_HOST
    els_port = settings.ELS_INFO.ELS_PORT
    try:
        index = index_set(host=els_host, port=els_port)
        index.delete(index_nm)
        index.create(index_nm)

        docmanager = default_search_set(host=els_host, port=els_port, index=index_nm)

        with db.get_db_manager() as session:
            select_query = CkanDataTable.get_select_query("")
            select_query.pop("where_info")
            ckan_list = session.query(**select_query).all()[0]

        logger.info(len(ckan_list))

        for ckan in ckan_list:
            docmanager.set_body(default_process(ckan))
            logger.info(docmanager.insert(ckan["biz_dataset_id"]))
    except Exception as e:
        print(e)
