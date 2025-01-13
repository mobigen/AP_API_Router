import logging
from datetime import datetime

from batch_service.app.common.const import SeoulDataKor, SeoulDataKorKatech, SeoulDataWorld, SeoulDataWorldKatech
from batch_service.app.database.conn import seoul_db, db

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
