import uuid
from typing import Dict
from Utils.CommonUtil import get_exception_info
from pydantic import BaseModel
from ELKSearch.Manager.manager import ElasticSearchManager


class BizMeta(BaseModel):
    biz_dataset_id: str
    src_url: str
    kywrd: str
    ctgry: str
    data_updt_cyc: str
    adm_dep: str
    admr_nm: str
    file_read_authority: str
    retv_num: str
    data_desc: str
    data_prv_desk: str
    license: str
    lang: str
    adm_dep_hp: str
    data_nm: str
    updt_nxt_dt: str
    updt_dt: str
    reg_dt: str
    reg_user: str
    amd_user: str
    reg_date: str
    amd_date: str
    data_shap: str
    data_srttn: str
    data_limit: str
    othr_use_notes: str
    data_eng_nm: str
    downl_num: str
    attnt_data_num: str
    share_num: str
    contents: str


def api(biz_meta_data: BizMeta) -> Dict:
    uid = uuid.uuid4()
    try:
        es = ElasticSearchManager()
        biz_meta_data = biz_meta_data.dict()
        biz_meta_data["biz_dataset_id"] = uid
        es.insert(biz_meta_data, biz_meta_data["biz_dataset_id"])

    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = {"result": 1, "errorMessage": ""}
    return result
