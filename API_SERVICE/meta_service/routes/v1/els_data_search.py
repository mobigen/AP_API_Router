import logging

from fastapi import APIRouter

from meta_service.database.conn import db
from libs.database.connector import Connector

from meta_service.ELKSearch.config import dev_server
from meta_service.ELKSearch.model import InputModel
from meta_service.ELKSearch.Utils.base import make_format
from meta_service.ELKSearch.Utils.document_utils import search_filter

from meta_service.common.search import default_search_set, base_query


router = APIRouter()

logger = logging.getLogger()

@router.post("/search")
def search(input: InputModel):
    """

    :param input:
    :return:
    """
    try:
        len_search = len(input.searchOption)
        len_filter = len(input.filterOption)
        docmanager = default_search_set(dev_server, input.index, input.size, input.from_)

        if not any([len_filter,len_search]):
            body = make_format("query","match_all",dict())
        else:
            search_query = base_query(len_search, input.searchOption)
            filter_query = base_query(len_filter, input.filterOption)
            body = make_format("query","bool", {"must": search_query,"filter": filter_query})

        docmanager.set_body(body)
        logger.info(body)
        data = {"header": "", "count": docmanager.count(body), "body": search_filter(docmanager.find(input.resultField))}
        result = {"result": 1, "data": data}
    except Exception as e:
        result = {"result": 0, "errorMessage": str(e)}
        logger.error(e, exc_info=True)
    return result
