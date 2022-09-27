from typing import Dict
from ServiceUtils.CommonUtil import connect_db, make_res_msg, get_exception_info


def api() -> Dict:
    meta_name_query = "SELECT\
                          CASE\
                              WHEN(SELECT tbmm.nm_id FROM tb_biz_meta_map tbmm WHERE tbmn.nm_id=tbmm.nm_id) IS NULL THEN 0\
                              ELSE 1\
                              END AS use_meta,\
                          tbmn.kor_nm,\
                          tbmn.eng_nm,\
                          tbmn.show_odrg,\
                          CASE\
                              WHEN tbmn.type = 0 THEN 'text'\
                              WHEN tbmn.type = 1 THEN 'int'\
                              WHEN tbmn.type = 2 THEN 'binary'\
                              END AS type,\
                          tbmn.nm_id\
                      FROM tb_biz_meta_name tbmn\
                      ORDER BY tbmn.nm_id;"

    try:
        db = connect_db()
        meta_name = db.select(meta_name_query)
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = make_res_msg(1, "", meta_name[0], meta_name[1])
    return result
