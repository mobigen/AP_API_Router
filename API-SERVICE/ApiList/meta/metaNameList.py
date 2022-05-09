from select import select
from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db

def api(perPage:int, curPage:int) -> Dict:
    db = connect_db(config.db_type, config.db_info)
    
    curPage = curPage - 1
    meta_name_query = f"""
    select *
    from metasch.tb_biz_meta_name as p
      join (SELECT kor_name,
            eng_name,
            show_order,
            name_id,
            (case
                  when type = 0 then 'text'
                  when type = 1 then 'int'
                  when type = 2 then 'binary'
                end
                ) as type,
            ROW_NUMBER () OVER (ORDER BY name_id DESC) as rowNo
      FROM tb_biz_meta_name
      order by name_id
          limit {perPage}
          offset ({perPage} * {curPage})
      ) as t on p.name_id = t.name_id
    """
    meta_name = db.select(meta_name_query)

    v_meta_name_query = "SELECT * FROM v_biz_meta_name;"
    v_meta_name = db.select(v_meta_name_query)

    return {"result" : "", "errorMessage" : "", "data": {"body": meta_name[0], "header": v_meta_name[0]}}