from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db
from Utils.DataBaseUtil import convert_data


def api() -> Dict:
    db = connect_db(config.db_type, config.db_info)
    category_query = "select * \
                      from metasch.tb_category \
                      order by parent_id, node_id;"
    category_list = db.select(category_query)[0]
    return {"result" : "", "errorMessage" : "", "data": category_list}