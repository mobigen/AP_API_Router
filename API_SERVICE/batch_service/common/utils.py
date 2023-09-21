import re
from datetime import datetime

from batch_service.ELKSearch.Utils.base import set_els
from batch_service.ELKSearch.document import DocumentManager


def default_search_set(server_config, index, size=10, from_=0):
    """
    검색에 필요한 default 세팅
    자동완성과 검색에 사용
    """
    es = set_els(server_config)
    docmanger = DocumentManager(es, index)
    docmanger.set_pagination(size, from_)
    return docmanger


def data_process(row):
    insert_body = dict()
    row["re_ctgry"] = re.sub("[ ]", "", str(row["ctgry"]))
    row["re_data_shap"] = re.sub("[ ]", "", str(row["data_shap"]))
    row["re_data_prv_desk"] = re.sub("[ ]", "", str(row["data_prv_desk"]))
    if "updt_dt" in row.keys() and row["updt_dt"] and len(row["updt_dt"]) > 25:
        if row["updt_dt"][-3:] == "+09":
            row["updt_dt"] = row["updt_dt"][:-3]
        row["updt_dt"] = datetime.strptime(row["updt_dt"], "%Y-%m-%d %H:%M:%S.%f")
    insert_body = row
    insert_body = default_process(insert_body)
    return insert_body


def default_process(insert_body):
    insert_body["_id"] = insert_body["biz_dataset_id"]
    insert_body["_source"] = insert_body
    insert_body["_source"]["biz_dataset_id"] = insert_body["biz_dataset_id"]