import logging
from datetime import datetime

from batch_service.app.common.const import SeoulDataKor, SeoulDataWorld
from batch_service.app.database.conn import seoul_db, db

logger = logging.getLogger()


def insert_ddr(kor_check: bool = True):
    # seoul_db -> katech_db
    try:
        if kor_check:
            table = SeoulDataKor
        else:
            table = SeoulDataWorld

        query = table.get_select_query("")
        query.pop("where_info")

        with seoul_db.get_db_manager() as session:
            dataset = session.query(**query).all()[0]

        logger.info(len(dataset))

        with db.get_db_manager() as sess:
            for data_dict in dataset:
                check_query = table.get_select_query(data_dict[table.key_column])
                if sess.query(**check_query).first():
                    # update
                    logger.info("update")
                    query = table.get_execute_query("update",data_dict)
                else:
                    #insert
                    logger.info("insert")
                    query = table.get_execute_query("insert",data_dict)

                logger.info(sess.execute(**query))

    except Exception as e:
        logger.info(data_dict)
        print(e)
