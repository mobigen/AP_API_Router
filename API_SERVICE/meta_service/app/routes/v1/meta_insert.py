import base64
import logging
import os

from fastapi import APIRouter, Depends

from libs.database.connector import Executor
from meta_service.app.common.const import MetaTempTable, MetaHtmlTable
from meta_service.app.database.conn import db

router = APIRouter()
logger = logging.getLogger()


def print_files_in_dir(root_dir, file_name):
    files = os.listdir(root_dir)
    print(len(files))
    for file in files:
        path = os.path.join(root_dir, file, file_name)
        print(path)


@router.get("/metaInsert")
def update_category(session: Executor = Depends(db.get_db)):
    eda_path = "/Users/cbc/Downloads/EDA_FILE"
    try:
        files = os.listdir(eda_path)
        id_cnt = 0
        for index, rid in enumerate(files):
            print(index)
            path = os.path.join(eda_path, rid, "profile_report_merged.html")
            with open(path, "rb") as fd:
                data = fd.read()
                data_base64 = base64.b64encode(data).decode("ascii")
                insert_data = f"data:text/html;base64,{data_base64}"
                print(f"LEN : {len(insert_data)}")

                select_res = session.query(**MetaTempTable.get_select_query(rid)).first()
                if select_res:
                    biz_dataset_id = select_res["biz_dataset_id"]
                    data = {"biz_dataset_id": biz_dataset_id, "file_data": insert_data}
                    session.execute(**MetaHtmlTable.get_execute_query("INSERT", data))
                else:
                    id_cnt += 1
            print(f"id_cnt : {id_cnt}")

        result = {"result": 1, "errorMessage": ""}
    except Exception as e:
        result = {"result": 0, "errorMessage": str(e)}
        logger.error(e, exc_info=True)
    return result
