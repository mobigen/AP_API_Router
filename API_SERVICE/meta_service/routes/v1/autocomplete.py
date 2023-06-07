import logging

from fastapi import APIRouter

from meta_service.database.conn import db
from libs.database.connector import Connector

from meta_service.ELKSearch.config import dev_server
from meta_service.ELKSearch.model import CoreOption
from meta_service.ELKSearch.Utils.base import make_format
from meta_service.ELKSearch.Utils.document_utils import search_filter

from meta_service.common.search import default_search_set, base_query


from pydantic import BaseModel


class Prefix(BaseModel):
    index: str
    size: int
    col_nm: str
    keyword: str


router = APIRouter()

logger = logging.getLogger()


@router.post("/autocomplete", response_model=dict)
def autocomplete(input: CoreOption, index: str, size: int):
    #input.field는 list 형식으로 받아야함, keywords는 string으로 받아야함
    try:
        
        docmanager = default_search_set(dev_server, index, size)
        if len(input.field) > 1:
            # multi field 일 때
            logger.info("multi_match")
            prefix_query = base_query(1, [input])
            
            for query_dict in prefix_query:
                query_dict["multi_match"].pop("operator",None)
            
            body = make_format("query","bool",{"must": prefix_query})
            docmanager.set_body(body)
            prefix_dict = search_filter(docmanager.find(input.field))

            if not len(prefix_dict):
                return {"result": 1,"data": []}

            prefix_data = [ word for data in prefix_dict for word in data.values() if input.keywords[0] in word]
        else:
            # 단일 field 일 때
            logger.info("prefix")
            field = input.field[0]
            query = {field: input.keywords}
            prefix_data = search_filter(docmanager.prefix(body=query, source=input.field))

            if not len(prefix_data):
                return {"result": 1,"data": []}

            prefix_data = [data[input.field[0]] for data in prefix_data]

        result = {"result": 1,"data": prefix_data}
        
    except Exception as e:
        result = {"result": 0, "errorMessage": str(e)}
        logger.error(e, exc_info=True)

    return result
