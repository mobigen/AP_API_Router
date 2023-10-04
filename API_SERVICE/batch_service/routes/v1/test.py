import logging
from fastapi import Depends, APIRouter
from copy import deepcopy

from batch_service.database.conn import seoul_db, db
from batch_service.common.const import DatasetDomesticTable, ResourceReportTable
from libs.database.connector import Connector


router = APIRouter()

logger = logging.getLogger()


def insert_db(sess, table_nm, data_list, insert_query):
    for data in data_list:
        if table_nm == "tbdataset_domestic_recommendation":
            insert_data = dict()
            for key, value in data.items():
                if key in ["ds_id","title","updated_at"]:
                    insert_data[key] = value
                else:
                    rec = value.split(" ")
                    insert_data[key] = rec[0]
                    insert_data[f"{key}_score"] = rec[1][1:-1]

            insert_query["data"] = insert_data
        else:
            insert_data = deepcopy(data)
            del insert_data["profile_content"]
            insert_query["data"] = insert_data

        sess.execute(**insert_query)


@router.get("/seoul_test", response_model=dict)
def seoul_test(table_nm:str, s_sess: Connector = Depends(seoul_db.get_db), d_sess: Connector = Depends(db.get_db)):
    if table_nm == "tbdataset_domestic_recommendation":
        query = {
            "table_nm": "tbdataset_domestic_recommendation",
            # "page_info": {
            #     "per_page": 5,
            #     "cur_page": 1
            # }
        }
        insert_query = DatasetDomesticTable.get_execute_query("insert",{})
        len_data = 1
    else:
        # todo: 전체 입력코드 1, 날짜별 업데이트 코드 1개
        query = {
            "table_nm": "tbresource_report",
            "page_info": {
                "per_page": 1,
                "cur_page": 1
            }
        }
        insert_query = ResourceReportTable.get_execute_query("insert",{})
        len_data = 11746

    for i in range(1,len_data+1):
        if table_nm == "tbresource_report":
            query["page_info"]["cur_page"] = i
        data_list, item_len = s_sess.query(**query).all()
        insert_db(d_sess,table_nm, data_list, insert_query)

    return {"test": 200}
