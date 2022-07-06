from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_exception_info
from Utils.DataBaseUtil import convert_data


def api(groupId) -> Dict:
    get_code_info_query = f'SELECT code_id, code_nm \
                                FROM tb_code_detail \
                            WHERE code_group_id = {convert_data(groupId)};'
    try:
        db = connect_db(config.db_info)
        code_info = db.select(get_code_info_query)
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = code_info[0]
    return result
