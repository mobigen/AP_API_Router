from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, make_res_msg, get_exception_info


def api(perPage: int, curPage: int) -> Dict:
    curPage = curPage - 1
    meta_name_query = f"SELECT\
                            p.*\
                        FROM tb_biz_meta_name AS p\
                        JOIN (\
                            SELECT kor_nm,\
                                eng_nm,\
                                show_odrg,\
                                nm_id,\
                                (CASE\
                                    WHEN type = 0 THEN 'text'\
                                    WHEN type = 1 THEN 'int'\
                                    WHEN type = 2 THEN 'binary'\
                                    END\
                                    ) AS type,\
                                    ROW_NUMBER () OVER (ORDER BY nm_id DESC) AS rowNo\
                            FROM tb_biz_meta_name\
                            ORDER BY nm_id\
                            LIMIT {perPage}\
                            OFFSET ({perPage} * {curPage})\
                        ) AS t ON p.nm_id = t.nm_id"
    total_cnt_query = "SELECT count(*) AS totalCount FROM tb_biz_meta_name"

    try:
        db = connect_db()
        meta_name = db.select(meta_name_query)
        total_cnt = db.select(total_cnt_query)
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = make_res_msg(1, "", meta_name[0], meta_name[1])
        result["data"].update(total_cnt[0][0])
    return result
