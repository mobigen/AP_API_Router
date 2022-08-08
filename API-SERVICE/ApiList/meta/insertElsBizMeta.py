import uuid
from typing import Dict
from Utils.CommonUtil import get_exception_info
from pydantic import BaseModel
from Utils.ESUtils import connect_es


class BizMeta(BaseModel):
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


def api(biz_meta_data: BizMeta) -> Dict:
    uid = uuid.uuid4()
    index = "biz_meta"
    try:
        es = connect_es()

        biz_meta_data = biz_meta_data.dict()
        biz_meta_data["biz_dataset_id"] = uid
        es.index(index=index,body=biz_meta_data)

    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = {"result": 1, "errorMessage": ""}
    return result
