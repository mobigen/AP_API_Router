from typing import Dict
from fastapi.logger import logger
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_exception_info
from Utils.DataBaseUtil import convert_data
from pydantic import BaseModel
import uuid


class createTable(BaseModel):
    ctgry: str
    table_nm: str


# column_type : number | string | time
# constraint : primary key, unique, not null
default_info = {
    "default_columns": [

    ]
}
'''
        {
            "eng_nm": "use_dataset_id",
            "kor_nm": "활용 데이터셋 아이디",
            "type": "string",
            "constraint": ["primary key"]
        },
        {
            "eng_nm": "apyr",
            "kor_nm": "신청자",
            "type": "string",
            "length": 64,
            "constraint": ["not null"]
        }
'''


def make_default_column(default_info):
    default_columns = ["idx serial4 not null"]
    for info in default_info:
        default_columns.append(
            f'{info["eng_nm"]} {info["type"]} {" ".join(info["constraint"])}')

    return default_columns


def make_ddl(category: str, table_name: str, config: Dict):
    default_info = config["default_columns"]
    default_columns = make_default_column(default_info)

    ddl = f'CREATE TABLE {category}.{table_name} ({",".join(default_columns)});'

    return ddl


def make_column_info(table_id, config):
    column_info_query = []
    default_info = config["default_columns"]
    for info in default_info:
        column_info_query.append(f'INSERT INTO tb_table_column_info (table_id, kor_nm, eng_nm) \
                                          VALUES ({convert_data(table_id)}, \
                                                  {convert_data(info["kor_nm"])}, \
                                                  {convert_data(info["eng_nm"])});')
    return column_info_query


def api(create_table: createTable) -> Dict:
    category = create_table.ctgry.lower()
    table_name = create_table.table_nm.lower()

    try:
        db = connect_db()
        ddl = make_ddl(category, table_name, default_info)
        db.execute(f"DROP TABLE IF EXISTS {table_name}")
        db.execute(ddl)

        table_id = uuid.uuid4()
        table_info_query = f'INSERT INTO tb_table_list (table_nm, id) \
                                    VALUES ({convert_data(table_name)}, {convert_data(table_id)});'
        db.execute(table_info_query)

        column_info_query = make_column_info(table_id, default_info)
        for query in column_info_query:
            db.execute(query)
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = {"result": 1, "errorMessage": ""}

    return result
