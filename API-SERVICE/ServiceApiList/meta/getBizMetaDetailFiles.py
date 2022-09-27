from typing import Dict
from ServiceUtils.CommonUtil import connect_db, make_res_msg, get_exception_info, convert_data


def api(datasetId: str = None) -> Dict:
    v_meta_files_query = f'SELECT * FROM tb_meta_detail_files WHERE biz_dataset_id = {convert_data(datasetId)}'

    try:
        db = connect_db()
        meta_files = db.select(v_meta_files_query)
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = make_res_msg(1, "", meta_files[0], meta_files[1])

    return result
