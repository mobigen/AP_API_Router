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
    fields: list
    query: str


router = APIRouter()

logger = logging.getLogger()


@router.post("/autocomplete", response_model=dict)
def autocomplete(input: Prefix):
    """
    :param input:
    {
        "index": "index_name",
        "size": 5,
        "fields": [
            "col1", "col2"
        ],
        "query": "search keyword"
    }
    :return:
    {
        "result": 1,
        "data": ["data1","data2"..."data5"]
    }
    """
    try:
        keyword = input.query
        docmanager = default_search_set(dev_server, input.index, input.size)
        input.query = f"(*{input.query}*)"
        del input.index
        del input.size
        
        body = make_format("query","query_string",input.dict())
        docmanager.set_body(body)
        prefix_dict = search_filter(docmanager.find(input.fields))

        if not len(prefix_dict):
            return {"result": 1,"data": []}

        prefix_data = [ word for data in prefix_dict for word in data.values() if keyword in word]
        # 데이터셋에서 해당 되는 데이터가 여러개 있을 수 있어 prefix_data에 size를 줌
        result = {"result": 1,"data": prefix_data[:docmanager.size]}
    except Exception as e:
        result = {"result": 0, "errorMessage": str(e)}
        logger.error(e, exc_info=True)

    return result
