from typing import Dict
from fastapi.logger import logger
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_token_info, make_res_msg
from starlette.requests import Request


def api(request: Request) -> Dict:
    user_info = get_token_info(request.headers)

    get_use_data_query = f'SELECT * FROM tb_board_use;'
    get_column_info = f"SELECT eng_nm, kor_nm FROM tb_board_column_info \
                                              WHERE table_id = (SELECT id FROM tb_board_name WHERE table_nm = 'tb_board_use');"

    try:
        db = connect_db(config.db_info)
        use_data, eng_columns = db.select(get_use_data_query)
        logger.error(f'USE DATA : {use_data}')
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        column_info, _ = db.select(get_column_info)
        kor_nm_list = [map_data["kor_nm"] for map_data in column_info]
        eng_nm_list = [map_data["eng_nm"] for map_data in column_info]

        result = make_res_msg(1, "", use_data, eng_nm_list, kor_nm_list)
    return result
