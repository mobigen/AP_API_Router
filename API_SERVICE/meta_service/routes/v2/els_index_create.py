import logging
import decimal

from fastapi import Depends, APIRouter

from meta_service.ELKSearch.config import dev_server
from meta_service.ELKSearch.Utils.base import set_els
from meta_service.ELKSearch.index import Index

router = APIRouter()

logger = logging.getLogger()


@router.post("/els-index-create", response_model=dict)
def els_update(index: str):
    try:
        es = set_els(dev_server)
        ind_manager = Index(es)
        indices = ind_manager.all_index().keys()
        if index not in indices:
            logger.info(ind_manager.create(index))
            result = {"result": 1,"data": "success"}

    except Exception as e:
        result = {"result": 0, "errorMessage": str(e)}
        logger.error(e, exc_info=True)
    return result

