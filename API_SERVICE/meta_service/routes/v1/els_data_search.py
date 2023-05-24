import logging

from fastapi import APIRouter

from meta_service.database.conn import db
from libs.database.connector import Connector
from meta_service.ELKSearch.config import local_server
from meta_service.ELKSearch.model import InputModel, CoreOption
from meta_service.ELKSearch.document import DocumentManager
from meta_service.ELKSearch.Utils.base import set_els, make_format


router = APIRouter()

logger = logging.getLogger()


@router.post("search", response_model=dict)
def search(input: InputModel):
    """

    :param input:
    :return:
    """
    index = "kt_biz_meta"
    try:
        es = set_els(local_server)
        docmanager = DocumentManager(es, index)
        docmanager.set_pagination(input.size, input.from_)

        # 임시
        search_option = CoreOption(**input.searchOption[0])
        search_query = make_format(
            "query",
            "match",
            {search_option.field[0]: search_option.keywords[0]}
        )

        docmanager.search()
    except Exception as e:
        result = {"result": 0, "errorMessage": str(e)}
        logger.error(e, exc_info=True)
    return result
