import uuid
from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_exception_info, convert_data
from pydantic import BaseModel


class insertBizMetaData(BaseModel):
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


def api(biz_meta_data: insertBizMetaData) -> Dict:
    uid = uuid.uuid4()
    get_column_info = 'SELECT item_id, eng_nm FROM v_biz_meta;'

    try:
        db = connect_db()
        column_info, _ = db.select(get_column_info)

        biz_meta_data = biz_meta_data.dict()
        insert_values = []
        for info in column_info:
            values = f'({convert_data(uid)}, {convert_data(info["item_id"])}, {convert_data(biz_meta_data[info["eng_nm"]])})'
            insert_values.append(values)

        insert_meta_query = f'INSERT INTO tb_biz_meta (biz_dataset_id, item_id, item_val) \
                                     VALUES {",".join(insert_values)};'
        db.execute(insert_meta_query)
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = {"result": 1, "errorMessage": ""}
    return result
