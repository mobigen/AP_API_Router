import logging

from fastapi import APIRouter

from meta_service.database.conn import db
from libs.database.connector import Connector

from meta_service.ELKSearch.config import dev_server
from meta_service.ELKSearch.model import InputModel
from meta_service.ELKSearch.Utils.base import make_format
from meta_service.ELKSearch.Utils.document_utils import search_filter

from meta_service.common.search import default_search_set


router = APIRouter()

logger = logging.getLogger()

@router.post("/search", response_model=dict)
def search(input: InputModel):
    """

    :param input:
    :return:
    """
    try:
        # 숫자 검색 조건에 포함
        docmanager = default_search_set(dev_server, input.index, input.size, input.from_)

        # 임시
        search_option = input.searchOption[0]
        search_query = make_format(
            "query",
            "match",
            {search_option.field[0]: search_option.keywords[0]}
        )

        docmanager.set_body(search_query)
        result = {"result": 0, "data": search_filter(docmanager.find(input.resultField))}
    except Exception as e:
        result = {"result": 0, "errorMessage": str(e)}
        logger.error(e, exc_info=True)
    return result
