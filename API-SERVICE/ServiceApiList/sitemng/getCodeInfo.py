from typing import Dict
from ServiceUtils.CommonUtil import connect_db, get_exception_info, convert_data


def api(groupId) -> Dict:
    get_code_info_query = f'SELECT code_id, code_nm \
                                FROM tb_code_detail \
                            WHERE code_group_id = {convert_data(groupId)};'
    try:
        db = connect_db()
        code_list = db.select(get_code_info_query)
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        code_info = []
        if len(code_list[0]):
            code_info = [{"code_id": code_detail["code_id"], "code_nm": code_detail["code_nm"]}
                         for code_detail in code_list[0]]

        body = {"list": code_info}
        result = {"result": 1, "errorMessage": "", "data": body}

    return result