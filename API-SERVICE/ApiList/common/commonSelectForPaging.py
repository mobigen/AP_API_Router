from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, make_res_msg, get_exception_info
from Utils.DataBaseUtil import convert_data


def api(table_nm: str, perPage: int, curPage: int) -> Dict:
    curPage = curPage - 1

    get_query = f'SELECT * FROM {table_nm}\
                           ORDER BY idx\
                           LIMIT {perPage}\
                           OFFSET ({perPage} * {curPage});'

    get_column_info = f"SELECT eng_nm, kor_nm FROM tb_table_column_info \
                                              WHERE table_id = (SELECT id FROM tb_table_list WHERE table_nm = {convert_data(table_nm)});"
    total_cnt_query = f"SELECT count(*) AS totalCount FROM {table_nm};"

    try:
        db = connect_db(config.db_info)
        use_data, _ = db.select(get_query)
        total_cnt = db.select(total_cnt_query)
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        column_info, _ = db.select(get_column_info)
        kor_nm_list = [map_data["kor_nm"] for map_data in column_info]
        eng_nm_list = [map_data["eng_nm"] for map_data in column_info]

        result = make_res_msg(1, "", use_data, eng_nm_list, kor_nm_list)
        result["data"].update(total_cnt[0][0])

    return result