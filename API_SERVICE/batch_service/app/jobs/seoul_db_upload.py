import logging
from datetime import datetime

from batch_service.app.common.const import SeoulDataKor, SeoulDataKorKatech, SeoulDataWorld, SeoulDataWorldKatech, BizDataTable, CkanDataTable
from batch_service.app.database.conn import seoul_db, db
from batch_service.app.common.config import settings, base_dir
from batch_service.app.common.utils import default_search_set, data_process, index_set
from libs.els.ELKSearch.Utils.base import set_els
from libs.els.ELKSearch.index import Index

logger = logging.getLogger()


def insert_db(kor_check: bool = True):
    # seoul_db -> katech_db
    try:
        if kor_check:
            table = SeoulDataKor
            table_katech = SeoulDataKorKatech
        else:
            table = SeoulDataWorld
            table_katech = SeoulDataWorldKatech

        query = table.get_select_query("")
        query.pop("where_info")

        with seoul_db.get_db_manager() as session:
            dataset = session.query(**query).all()[0]

        logger.info(f"Table = {table.table_nm}, Found Data Length = {len(dataset)}")

        update_index, insert_index = 0, 0
        with db.get_db_manager() as sess:
            for data_dict in dataset:
                data_dict["modified_dt"] = data_dict["cat_ver"]
                check_query = table_katech.get_select_query(data_dict[table.key_column])
                if sess.query(**check_query).first():
                    # update
                    update_index += 1
                    query = table_katech.get_execute_query("update",data_dict)
                else:
                    #insert
                    insert_index += 1
                    query = table_katech.get_execute_query("insert",data_dict)

                if not (update_index + insert_index) % 100 :
                    logger.info(f"Table = {table.table_nm}, Update = {update_index}, Insert = {insert_index} Processing...")

                sess.execute(**query)
        logger.info(f"Table = {table.table_nm}, Total Data = {update_index + insert_index} Processed")

    except Exception as e:
        logger.info(data_dict)
        print(e)


def init_els():
    es = set_els(host=settings.ELS_INFO.ELS_HOST, port=settings.ELS_INFO.ELS_PORT)
    logger.info(Index(es).init_els_all_index(f"{base_dir}/resources/mapping"))

    bulk_index("biz_meta", BizDataTable)
    bulk_index("v_biz_meta_oversea_els", CkanDataTable)

def bulk_index(index_nm, table):
    try:
        docmanager = default_search_set(host=settings.ELS_INFO.ELS_HOST, port=settings.ELS_INFO.ELS_PORT, index=index_nm)

        query = table.get_select_query("")
        query.pop("where_info")
        with db.get_db_manager() as sess:
            data_list = sess.query(**query).all()[0]
            logger.info(len(data_list))

            for data_dict in data_list:
                insert_body = data_process(data_dict)
                docmanager.set_body(insert_body["_source"])
                res = docmanager.insert(insert_body["_id"])
                logger.info(res)
    except Exception as e:
        logger.info(e)
        print(e)

