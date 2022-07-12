from typing import Dict, List
from fastapi.logger import logger
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db
from Utils.DataBaseUtil import convert_data
from pydantic import BaseModel
from starlette.requests import Request


class addTableColumn(BaseModel):
    table_nm: str
    eng_nm: str
    kor_nm: str
    data_type: str

# column_type : number | string | time | auto_index
# constraint : primary key, unique, not null


def get_type(data_type, length=None):
    if data_type == "number":
        column_type = "int4"
    elif data_type == "string":
        if length:
            column_type = f'varchar({length})'
        else:
            column_type = "varchar"
    elif data_type == "time":
        column_type = "timestamp"
    else:
        raise Exception(f"Invalid type ({data_type})")
    return column_type


def api(add_table_columns: List[addTableColumn]) -> Dict:
    try:
        db = connect_db(config.db_info)

        for add_table_column in add_table_columns:
            table_name = add_table_column.table_nm.lower()

            data_type = get_type(add_table_column.data_type)

            add_column_query = f'ALTER TABLE {table_name} ADD {add_table_column.eng_nm} {data_type};'
            db.execute(add_column_query)

            get_table_id_query = f'SELECT id FROM tb_table_list WHERE table_nm = {convert_data(table_name)};'
            result, _ = db.select(get_table_id_query)
            table_id = result[0]["id"]
            column_info_query = f'INSERT INTO tb_table_column_info (table_id, kor_nm, eng_nm) \
                                        VALUES ({convert_data(table_id)}, \
                                                {convert_data(add_table_column.kor_nm)}, \
                                                {convert_data(add_table_column.eng_nm)});'
            db.execute(column_info_query)
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        result = {"result": 1, "errorMessage": ""}

    return result
