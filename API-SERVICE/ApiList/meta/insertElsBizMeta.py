import uuid
from typing import Dict
from Utils.CommonUtil import get_exception_info
from pydantic import BaseModel
from Utils.ESUtils import connect_es


class BizMeta(BaseModel):
    adm_dep: str
    adm_dep_hp: str
    admr_nm: str
    copyright: str
    ctgry: str
    data_desc: str
    data_nm: str
    data_prv_desk: str
    data_shap: str
    data_updt_cyc: str
    file_read_authority: str
    file_type: str
    kywrd: str
    lang: str
    license: str
    reg_date: str
    retv_num: str
    rqt_dep: str
    src_sys: str
    src_url: str
    updt_date: str
    updt_nxt_date: str


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
