from typing import Dict
from fastapi.logger import logger
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db
from Utils.DataBaseUtil import convert_data
from pydantic import BaseModel


class deleteTable(BaseModel):
    table_nm: str

# column_type : number | string | time
# constraint : primary key, unique, not null


def api(delete_table: deleteTable) -> Dict:
    table_name = delete_table.table_nm.lower()

    drop_query = f'DROP TABLE {table_name};'
    delete_board_name = f'DELETE FROM tb_table_list WHERE table_nm = {convert_data(table_name)};'
    try:
        db = connect_db(config.db_info)
        db.execute(drop_query)
        db.execute(delete_board_name)
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        result = {"result": 1, "errorMessage": ""}

    return result
