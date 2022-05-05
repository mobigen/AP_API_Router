from typing import Dict, Optional
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db
from Utils.DataBaseUtil import convert_data
from pydantic import BaseModel


class UpdateCategory(BaseModel):
    parent_id: Optional[str] = None
    node_id: Optional[str] = None
    node_name: str


# todo: 수정 필요
def api(update:UpdateCategory) -> Dict:
    db = connect_db(config.db_type, config.db_info)
    
    if update.node_id:    
        query = f'UPDATE tb_biz_meta_name\
                  SET parent_id   = {convert_data(update.parent_id)},\
                      node_id   = {convert_data(update.node_id)},\
                      node_name = {convert_data(update.node_name)}\
                  WHERE node_id = {convert_data(update.node_id)};'
    else:
        query = f'UPDATE tb_biz_meta_name\
                  SET parent_id   = {convert_data(update.parent_id)},\
                      node_id   = {convert_data(update.node_id)},\
                      node_name = {convert_data(update.node_name)}\
                  WHERE parent_id = {convert_data(update.parent_id)} and \
                        node_name = {convert_data(update.node_name)};'

    db.execute(query)
    return {"result" : "", "errorMessage" : ""}