from datetime import datetime

from fastapi.logger import logger
from fastapi import APIRouter, Depends

from batch_service.app.common.const import BizDataTable, CkanDataTable, SeoulDataKor, SeoulDataWorld
from batch_service.app.database.conn import db, seoul_db

from libs.database.orm import Executor

router = APIRouter()


@router.post("/update_seoul_db")
async def seoul_test(kor_check: bool = True, session: Executor = Depends(db.get_db)):
    # seoul_db -> katech_db
    st = datetime.now()
    try:
        if kor_check:
            table = SeoulDataKor
        else:
            table = SeoulDataWorld

        query = table.get_select_query("")
        query.pop("where_info")
        with seoul_db.get_db_manager() as sess:
            dataset = sess.query(**query).all()[0]
        logger.info(len(dataset))

        for data_dict in dataset:
            check_query = table.get_select_query(data_dict[table.key_column])
            if session.query(**check_query).first():
                # update
                query = table.get_execute_query("update",data_dict)
                logger.info(data_dict["ds_id"])
            else:
                #insert
                query = table.get_execute_query("insert",data_dict)
                logger.info(data_dict["ds_id"])

            session.execute(**query)
        et = datetime.now()
        logger.info(len(dataset))
        logger.info(et - st)

    except Exception as e:
        print(e)