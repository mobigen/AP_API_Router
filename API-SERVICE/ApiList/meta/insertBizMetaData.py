import uuid
from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_token_info
from Utils.DataBaseUtil import convert_data
from fastapi.logger import logger
from starlette.requests import Request
from pydantic import BaseModel


class insertBizMetaData(BaseModel):
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


def api(biz_meta_data: insertBizMetaData, request: Request) -> Dict:
    user_info = get_token_info(request.headers)

    uid = uuid.uuid4()
    get_column_info = 'SELECT item_id, eng_nm FROM v_biz_meta;'

    try:
        db = connect_db(config.db_info)
        column_info, _ = db.select(get_column_info)

        biz_meta_data = biz_meta_data.dict()
        insert_values = []
        for info in column_info:
            values = f'({convert_data(uid)}, {convert_data(info["item_id"])}, {convert_data(biz_meta_data[info["eng_nm"]])})'
            insert_values.append(values)

        insert_meta_query = f'INSERT INTO tb_biz_meta (biz_dataset_id, item_id, item_val) \
                                     VALUES {",".join(insert_values)};'
        db.execute(insert_meta_query)
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        result = {"result": 1, "errorMessage": ""}
    return result
