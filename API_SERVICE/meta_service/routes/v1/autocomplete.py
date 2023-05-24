import logging

from fastapi import APIRouter

from meta_service.database.conn import db
from libs.database.connector import Connector
from meta_service.ELKSearch.config import local_server
from meta_service.common.search import common_prefix

from pydantic import BaseModel


class Prefix(BaseModel):
    size: int
    col_nm: str
    keyword: str


router = APIRouter()

logger = logging.getLogger()


@router.post("autocomplete", response_model=dict)
def autocomplete(input: Prefix):
    index = ""

    try:
        result = common_prefix(local_server, index, input)
    except Exception as e:
        result = {"result": 0, "errorMessage": str(e)}
        logger.error(e, exc_info=True)
    return result
