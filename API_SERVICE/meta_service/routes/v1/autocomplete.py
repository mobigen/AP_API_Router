import logging

from fastapi import APIRouter

from meta_service.database.conn import db
from libs.database.connector import Connector

from meta_service.ELKSearch.config import dev_server
from meta_service.ELKSearch.Utils.document_utils import search_filter

from meta_service.common.search import default_search_set


from pydantic import BaseModel


class Prefix(BaseModel):
    index: str
    size: int
    col_nm: str
    keyword: str


router = APIRouter()

logger = logging.getLogger()


@router.post("/autocomplete", response_model=dict)
def autocomplete(input: Prefix):
    try:
        query = {input.col_nm: input.keyword}
        docmanager = default_search_set(dev_server, input.index, input.size)
        prefix_data = search_filter(docmanager.prefix(body=query, source=[input.col_nm]))
        prefix_data = [data[input.col_nm] for data in prefix_data]
        result = {"result": 1,"dataList": prefix_data}
    except Exception as e:
        result = {"result": 0, "errorMessage": str(e)}
        logger.error(e, exc_info=True)
    return result
