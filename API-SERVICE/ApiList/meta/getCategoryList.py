from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db
from Utils.DataBaseUtil import convert_data

'''
    <!-- category 목록 조회-->
    <select id="getCategoryList" resultType="java.util.Map">
        select *
        from metasch.tb_category
        order by parent_id, node_id;
    </select>
'''

def api() -> Dict:
    db = connect_db(config.db_type, config.db_info)

    return {"API_NAME" : "TEST"}