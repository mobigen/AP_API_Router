# import logging

from fastapi import APIRouter

from meta_service.database.conn import db
from libs.database.connector import Connector

from meta_service.ELKSearch.config import local_server
from meta_service.ELKSearch.Utils.document_utils import search_filter

from meta_service.common.search import default_search_set


from pydantic import BaseModel, Field


class Prefix(BaseModel):
    index: str
    size: int
    from_: int = Field(0, alias="from")
    col_nm: str
    keyword: str


router = APIRouter()

# logger = logging.getLogger()


@router.post("/autocomplete", response_model=dict)
def autocomplete(input: Prefix):
    try:
        query = {input.col_nm: input.keyword}
        docmanager = default_search_set(local_server, input.index, input.size)
        result = {"result": 0,"data": search_filter(docmanager.prefix(body=query))}
    except Exception as e:
        result = {"result": 0, "errorMessage": str(e)}
        # logger.error(e, exc_info=True)
    return result
