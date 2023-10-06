import logging
from datetime import datetime
from copy import deepcopy

from batch_service.database.conn import seoul_db, db
from batch_service.common.const import DatasetDomesticTable, ResourceReportTable


logger = logging.getLogger()
today = datetime.today().strftime("%Y-%m-%d")


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


def insert_ddr():
    # upload tbdataset_domestic_recommendation
    table_nm = "tbdataset_domestic_recommendation"
    query = {
        "table_nm": table_nm
    }
    insert_query = DatasetDomesticTable.get_execute_query("insert",{})

    with seoul_db.get_db_manager() as session:
        data_list, item_len = session.query(**query).all()

    with db.get_db_manager() as session:
        insert_db(session,table_nm, data_list, insert_query)


def insert_rr():
    """
    upload tbresource_report
    데이터가 커서 1개씩 입력해야함

    :return:
    """
    i = 1
    table_nm = "tbresource_report"
    query = {
        "table_nm": table_nm,
        "page_info": {
            "per_page": 1,
            "cur_page": i
        }
    }
    update_query = ResourceReportTable.get_execute_query("update",{})
    with seoul_db.get_db_manager() as s_sess:
        with db.get_db_manager() as d_sess:
            while True:
                query["page_info"]["cur_page"] = i
                data_list, item_len = s_sess.query(**query).all()
                insert_db(d_sess, table_nm, data_list, update_query)
                if i == item_len:
                    break
                else:
                    i = i+1


def update_ddr():
    # upload tbdataset_domestic_recommendation
    table_nm = "tbdataset_domestic_recommendation"
    query = {
        "table_nm": table_nm,
        "key": ["ds_id"],
        "where_info": [
            {
                "table_nm": table_nm,
                "key": "updated_at",
                "value": today,
                "compare_op": ">",
                "op": ""
            }
        ]
    }

    with seoul_db.get_db_manager() as session:
        data_list, item_len = session.query(**query).all()

    update_query = DatasetDomesticTable.get_execute_query("update",data_list)

    with db.get_db_manager() as session:
        session.execute(**update_query)


def update_rr():
    """
    upload tbresource_report
    데이터가 커서 1개씩 입력해야함

    :return:
    """
    i = 1
    table_nm = "tbresource_report"
    query = {
        "table_nm": table_nm,
        "key": ["rp_id"],
        "where_info": [
            {
                "table_nm": table_nm,
                "key": "updated_at",
                "value": today,
                "compare_op": ">",
                "op": ""
            }
        ],
        "page_info": {
            "per_page": 1,
            "cur_page": i
        }
    }
    with seoul_db.get_db_manager() as s_sess:
        with db.get_db_manager() as d_sess:
            while True:
                query["page_info"]["cur_page"] = i
                data_list, item_len = s_sess.query(**query).all()
                update_query = ResourceReportTable.get_execute_query("update",data_list)
                d_sess.execute(**update_query)

                if i == item_len:
                    break
                else:
                    i = i+1
