import re
from datetime import datetime

from batch_service.ELKSearch.Utils.base import set_els
from batch_service.ELKSearch.document import DocumentManager
from batch_service.ELKSearch.index import Index


def default_search_set(server_config, index, size=10, from_=0):
    """
    검색에 필요한 default 세팅
    자동완성과 검색에 사용
    """
    es = set_els(server_config)
    docmanger = DocumentManager(es, index)
    docmanger.set_pagination(size, from_)
    return docmanger


def index_set(server_config):
    es = set_els(server_config)
    return Index(es)


def data_process(row):
    row["re_ctgry"] = re.sub("[ ]", "", str(row["ctgry"]))
    row["re_data_shap"] = re.sub("[ ]", "", str(row["data_shap"]))
    row["re_data_prv_desk"] = re.sub("[ ]", "", str(row["data_prv_desk"]))
    row = default_process(row)
    return row


def default_process(row):
    if "updt_dt" in row.keys() and row["updt_dt"] and len(row["updt_dt"]) > 25:
        if row["updt_dt"][-3:] == "+09":
            row["updt_dt"] = row["updt_dt"][:-3]
        row["updt_dt"] = datetime.strptime(row["updt_dt"], "%Y-%m-%d %H:%M:%S.%f")
    if "reg_date" in row.keys() and row["reg_date"] and len(row["reg_date"]) > 25:
        if row["reg_date"][-3:] == "+09":
            row["reg_date"] = row["reg_date"][:-3]
        row["reg_date"] = datetime.strptime(row["reg_date"], "%Y-%m-%d %H:%M:%S.%f")
    return row