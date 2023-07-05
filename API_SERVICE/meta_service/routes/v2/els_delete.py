import logging

from fastapi import APIRouter, Depends

from meta_service.ELKSearch.config import dev_server

from meta_service.common.search import Record, default_search_set


router = APIRouter()

logger = logging.getLogger()

@router.post("/els_delete")
def els_delete(input: Record):
    try:
        docmanager = default_search_set(dev_server, input.index)
        docmanager.delete(input.key,input.ids)


        result = {"result": 1, "data": "data"}
    except Exception as e:
        result = {"result": 0, "errorMessage": str(e)}
        logger.error(e, exc_info=True)
    return result
