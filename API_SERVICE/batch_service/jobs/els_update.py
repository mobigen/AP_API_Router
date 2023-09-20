import logging
from datetime import datetime

from batch_service.ELKSearch.config import dev_server
from batch_service.common.utils import default_search_set, data_process, default_process

from batch_service.database.conn import db
from batch_service.common.const import BizDataTable, CkanDataTable


logger = logging.getLogger()


def insert_meta():
    bulk_meta_item = list()
    docmanager = default_search_set(dev_server, "biz_meta")

    with db.get_db_manager() as session:
        meta_list = session.query(**BizDataTable.get_select_query("D")).all()
    try:
        for data in meta_list:
            insert_body = data_process(data)
            bulk_meta_item.append(insert_body)
            docmanager.set_body(insert_body)
            logger.info(docmanager.insert(insert_body["biz_dataset_id"]))
    except Exception as e:
        print(e)


def insert_ckan():
    bulk_meta_item = list()
    docmanager = default_search_set(dev_server, "ckan_data")
    with db.get_db_manager() as session:
        select_query = CkanDataTable.get_select_query("*")
        select_query.pop("where_info")
        ckan_list = session.query(**select_query).all()
    try:
        for ckan in ckan_list:
            insert_body = default_process(dict(), ckan)
            bulk_meta_item.append(insert_body)
            docmanager.set_body(insert_body)
            logger.info(docmanager.insert(insert_body["biz_dataset_id"]))
    except Exception as e:
        print(e)


