from datetime import datetime

from fastapi.logger import logger
from fastapi import APIRouter, Depends

from batch_service.app.common.const import BizDataTable, CkanDataTable, SeoulDataKor, SeoulDataWorld
from batch_service.app.common.utils import default_search_set, data_process, index_set
from batch_service.app.database.conn import db, seoul_db

from libs.database.orm import Executor

router = APIRouter()


@router.get("/update_meta_els")
async def meta_test(session: Executor = Depends(db.get_db)):
    index_nm = "biz_meta"
    els_host = "10.10.10.62"
    els_port = "39200"
    try:
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
