from datetime import datetime, timedelta

from fastapi.logger import logger
from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from batch_service.app.common.const import BizDataTable, CkanDataTable, SeoulDataKor, SeoulDataWorld
from batch_service.app.common.utils import default_search_set, data_process, index_set
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


@router.get("/update_meta_els")
async def meta_test(session: Executor = Depends(db.get_db)):
    index_nm = "biz_meta"
    els_host = "10.10.10.62"
    els_port = "39200"
    try:
        index = index_set(host=els_host, port=els_port)
        docmanager = default_search_set(host=els_host, port=els_port, index=index_nm)

        query = BizDataTable.get_select_query("D")
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


@router.get("/update_oversea_els")
async def oversea_test(session: Executor = Depends(db.get_db)):
    index_nm = "v_biz_meta_oversea_els"
    els_host = "10.10.10.62"
    els_port = "39200"
    try:
        index = index_set(host=els_host, port=els_port)
        docmanager = default_search_set(host=els_host, port=els_port, index=index_nm)

        query = CkanDataTable.get_select_query("")
        query.pop("where_info")
        oversea_list = session.query(**query).all()[0]
        logger.info(len(oversea_list))

        for oversea in oversea_list:
            insert_body = data_process(oversea)
            docmanager.set_body(insert_body["_source"])
            res = docmanager.insert(insert_body["_id"])
            logger.info(res)
    except Exception as e:
        print(e)


# els update condition
def time_check_cond(query, table_nm, date, op=""):
    query["where_info"].append({
        "table_nm": table_nm,
        "key": "modified_dt",
        "value": date,
        "compare_op": ">=",
        "op": op,
    })
    return query
