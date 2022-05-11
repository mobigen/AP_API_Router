from typing import Dict
from fastapi.logger import logger
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db
from Utils.DataBaseUtil import convert_data
from pydantic import BaseModel


class InsertMetaName(BaseModel):
    subscribed: bool
    kor_name: str
    eng_name: str
    show_order: int
    name_id: str
    type: int


def api(insert: InsertMetaName) -> Dict:
    query = f'INSERT INTO tb_biz_meta_name (kor_name, eng_name, show_order, name_id, type)\
                VALUES ({convert_data(insert.kor_name)}, {convert_data(insert.eng_name)}, {convert_data(insert.show_order)},\
                (SELECT concat(\'i\', CAST(substring(max(name_id), 2) AS INT) + 1) AS name_id FROM tb_biz_meta_name), {convert_data(insert.type)});'
    try:
        db = connect_db(config.db_type, config.db_info)
        db.execute(query)
    except Exception as err:
        # make error response
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        # make response
        result = {"result": 1, "errorMessage": ""}
    return result
