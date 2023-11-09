import logging

from fastapi import APIRouter, Depends
from meta_service.app.ELKSearch.Utils.base import make_format
from meta_service.app.ELKSearch.Utils.document_utils import search_filter
from meta_service.app.ELKSearch.config import dev_server
from meta_service.app.ELKSearch.model import InputModel
from meta_service.app.common.search import default_search_set, base_query
from meta_service.app.database.conn import db

from libs.database.connector import Connector

router = APIRouter()

logger = logging.getLogger()


@router.post("/search")
def search(input: InputModel, session: Connector = Depends(db.get_db)):
    """

    :param input:
    :return:
    """
    try:
        len_search = len(input.searchOption)
        len_filter = len(input.filterOption)

        # from_ 0 부터 시작해야함, web에서는 1부터 넘어오기 때문에 1을 빼준다
        docmanager = default_search_set(dev_server, input.index, input.size, input.from_ - 1)

        # query에 조건이 없으면 match all 실행
        if not any([len_filter, len_search]):
            body = make_format("query", "match_all", dict())
        else:
            search_query = base_query(len_search, input.searchOption)
            filter_query = base_query(len_filter, input.filterOption)
            body = make_format("query", "bool", {"must": search_query, "filter": filter_query})

        docmanager.set_body(body)
        data = {
            "header": session.get_column_info(input.index.upper()),
            "count": docmanager.count(body),
            "body": search_filter(docmanager.find(input.resultField)),
        }
        result = {"result": 1, "data": data}
    except Exception as e:
        result = {"result": 0, "errorMessage": str(e)}
        logger.error(e, exc_info=True)
    return result
