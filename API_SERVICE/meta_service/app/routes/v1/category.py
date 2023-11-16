import logging

from fastapi import Depends, APIRouter
from pydantic import BaseModel

from libs.database.connector import Executor
from libs.els.ELKSearch.Utils.base import make_format
from meta_service.app.common.config import settings
from meta_service.app.common.search import default_search_set
from meta_service.app.database.conn import db

router = APIRouter()
logger = logging.getLogger()


class UpdateCategory(BaseModel):
    node_id: str
    node_nm: str


@router.post("/updateCategory")
def update_category(update: UpdateCategory, session: Executor = Depends(db.get_db)):
    """
    현재 사용하지 않는 API
    구 버전과 동작은 동작은 같은 코드
    prnts_id 값을 uuid값으로 부여한다.
    """
    # table_nm = "tb_category"
    # data_query = {
    #     "table_nm": table_nm,
    #     "key": "*",
    #     "where_info": [
    #         {
    #             "table_nm": table_nm,
    #             "key": "node_id",
    #             "value": update.node_id,
    #             "op": "",
    #             "compare_op": "="
    #         }
    #     ]
    # }
    # try:
    #     # select
    #     row = session.query(**data_query).first()
    #     row["prnts_id"] = convert_data(uuid.uuid4())
    #     # update
    #     update_query = {
    #         "method": "UPDATE",
    #         "table_nm": table_nm,
    #         "data": row,
    #         "key": "node_id"
    #     }
    #     session.execute(**update_query)
    try:
        result = {"result": 1, "errorMessage": ""}
    except Exception as e:
        result = {"result": 0, "errorMessage": str(e)}
        logger.error(e, exc_info=True)
    return result


class DeleteData(BaseModel):
    biz_dataset_id: str


@router.get("/getCategoryNmCount")
def update_category(nms: str):
    """
    메인 페이지에 사용
    :param nms: 기타,미래차 산업, ....
    :return:
    """
    data_dict = {}
    index = "biz_meta,v_biz_meta_oversea_els"
    key = "re_ctgry"
    try:
        docmanager = default_search_set(settings.ELS_INFO.ELS_HOST, settings.ELS_INFO.ELS_PORT, index)
        ctgry_nm_list = nms.split(",")
        for c_id in ctgry_nm_list:
            c_v = c_id.replace(" ", "")
            cnt_query = make_format("query", "match_phrase", {key: c_v})
            cnt = docmanager.count(body=cnt_query)
            data_dict[c_id.replace(" ", "_")] = cnt
        result = {"result": 1, "errorMessage": "", "data": data_dict}
    except Exception as e:
        result = {"result": 0, "errorMessage": str(e)}
        logger.error(e, exc_info=True)
    return result
