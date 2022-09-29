from typing import Dict
from ServiceUtils.CommonUtil import connect_db, make_res_msg, get_exception_info, convert_data


def api(apyr: str) -> Dict:
    get_use_data_query = f'SELECT * FROM tb_board_use WHERE apyr = {convert_data(apyr)};'
    get_column_info = f"SELECT eng_nm, kor_nm FROM tb_board_column_info \
                                              WHERE table_id = (SELECT id FROM tb_board_name WHERE table_nm = 'tb_board_use');"

    try:
        db = connect_db()
        use_data, _ = db.select(get_use_data_query)
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        column_info, _ = db.select(get_column_info)
        kor_nm_list = [map_data["kor_nm"] for map_data in column_info]
        eng_nm_list = [map_data["eng_nm"] for map_data in column_info]

        result = make_res_msg(1, "", use_data, eng_nm_list, kor_nm_list)
    return result