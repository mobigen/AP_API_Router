from typing import Dict
from fastapi.logger import logger
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_token_info, make_res_msg
from Utils.DataBaseUtil import convert_data
from starlette.requests import Request


def api(use_dataset_id: str, request: Request) -> Dict:
    user_info = get_token_info(request.headers)

    get_use_data_query = f'SELECT * FROM tb_board_use WHERE use_dataset_id = {convert_data(use_dataset_id)};'
    get_column_info = f"SELECT eng_nm, kor_nm FROM tb_board_column_info \
                                              WHERE table_id = (SELECT id FROM tb_board_name WHERE table_nm = 'tb_board_use');"

    try:
        db = connect_db(config.db_info)
        use_data, eng_columns = db.select(get_use_data_query)
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        kor_nm_list = []
        name_info = {}
        column_info, _ = db.select(get_column_info)

        for name in column_info:
            name_info[name['eng_nm']] = name['kor_nm']
        for eng_nm in eng_columns:
            if eng_nm in name_info:
                kor_nm_list.append(name_info[eng_nm])
            else:
                kor_nm_list.append("")
        result = make_res_msg(1, "", use_data, eng_columns, kor_nm_list)
    return result
