from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_exception_info


def api() -> Dict:
    category_query = 'SELECT * FROM tb_category ORDER BY prnts_id, node_id;'

    try:
        db = connect_db()
        category_list = db.select(category_query)[0]
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = {"result": 1, "errorMessage": "", "data": category_list}
    return result
