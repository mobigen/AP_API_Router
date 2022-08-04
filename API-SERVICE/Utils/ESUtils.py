from elasticsearch import Elasticsearch
from pydantic import BaseModel


class ESBizMeta(BaseModel):
    biz_dataset_id: str
    adm_dep: str
    rqt_dep: str
    admr_nm: str
    rqt_nm: str
    ctgry: str
    reg_date: str
    ltst_amd_dt: str
    prv_shap: str
    file_size: str
    open_scope: str
    data_shap: str
    src_sys: str
    src_url: str
    kywrd: str
    data_prv_desk: str
    data_updt_cyc: str
    law_evl_conf_yn: str
    scrty_evl_conf_yn: str
    updt_nxt_date: str
    data_nm: str
    data_desc: str


def connect_es(host: str = "localhost",port: str = "9200"):
    es = Elasticsearch(f"http://{host}:{port}")
    return es


class ESSearch:
    pass
