from typing import Dict
from fastapi.logger import logger
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_exception_info
from Utils.DataBaseUtil import convert_data
from pydantic import BaseModel


class delTableColumn(BaseModel):
    table_nm: str
    eng_nm: str

# column_type : number | string | time
# constraint : primary key, unique, not null


def api(del_table_column: delTableColumn) -> Dict:
    table_name = del_table_column.table_nm.lower()

    del_column_query = f'ALTER TABLE {table_name} DROP {del_table_column.eng_nm};'

    try:
        db = connect_db()
        db.execute(del_column_query)

        get_table_id_query = f'SELECT id FROM tb_table_list WHERE table_nm = {convert_data(table_name)};'
        result, _ = db.select(get_table_id_query)

        table_id = result[0]["id"]
        column_info_query = f'DELETE FROM tb_table_column_info WHERE eng_nm={convert_data(del_table_column.eng_nm)} \
                                                AND table_id={convert_data(table_id)};'
        db.execute(column_info_query)
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = {"result": 1, "errorMessage": ""}

    return result
