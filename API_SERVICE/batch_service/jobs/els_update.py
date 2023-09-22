import logging

from batch_service.ELKSearch.config import dev_server

from batch_service.database.conn import db

from batch_service.common.const import BizDataTable, CkanDataTable
from batch_service.common.utils import default_search_set, data_process, default_process, index_set


logger = logging.getLogger()


def insert_meta():
    index_nm = "biz_meta"
    try:
        index = index_set(dev_server)
        index.delete(index_nm)
        index.create(index_nm)

        docmanager = default_search_set(dev_server, index_nm)

        with db.get_db_manager() as session:
            query = BizDataTable.get_select_query("")
            query.pop("where_info")
            meta_list = session.query(**query).all()[0]

        logger.info(len(meta_list))

        for meta in meta_list:
            insert_body = data_process(meta)
            docmanager.set_body(insert_body)
            logger.info(docmanager.insert(insert_body["biz_dataset_id"]))
    except Exception as e:
        print(e)


def insert_ckan():
    index_nm = "ckan_data"
    try:
        index = index_set(dev_server)
        index.delete(index_nm)
        index.create(index_nm)

        docmanager = default_search_set(dev_server, index_nm)

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


