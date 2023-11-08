import logging

from fastapi import APIRouter, Depends
from meta_service.app.ELKSearch.Utils.base import make_format
from meta_service.app.ELKSearch.Utils.document_utils import search_filter
from meta_service.app.ELKSearch.config import dev_server
from meta_service.app.ELKSearch.model import InputModel
from meta_service.app.common.config import settings
from meta_service.app.common.search import default_search_set, base_query
from meta_service.app.database.conn import db

from libs.database.connector import Connector

router = APIRouter()

logger = logging.getLogger()


@router.post("/search")
def search(input: InputModel, session: Connector = Depends(db.get_db)):
    """
    :param input:
    {
        "index": "index_name",
        "from": 0,    # page
        "size": 10,   # result size
        "resultField": ["col1", "col2"],
        "sortOption": [{"col": "desc"}],
        "searchOption": [
            {
                "field": ["conm"],
                "operator": "OR",
                "keywords": ["기업명"]
            }
        ],
        "filterOption": []
    }
    :return:
    {
        "result": 1,
        "data": {
            "header": {"column_name": "col1", "kor_column_name": "컬럼명1"},
            "count": "10",  # total count
            "body": [{data set 1}, {data set 2} ... {data set 10}]
        }
    }
    """
    try:
        len_search = len(input.searchOption)
        len_filter = len(input.filterOption)
        len_range = len(input.rangeOption)

        # from_ 0 부터 시작해야함, web에서는 1부터 넘어오기 때문에 1을 빼준다
        docmanager = default_search_set(dev_server, input.index, input.size, input.from_ - 1)

        # query에 조건이 없으면 match all 실행
        if not any([len_filter, len_search, len_range]):
            body = make_format("query", "match_all", dict())
        else:
            search_format = "(*{0}*)"
            search_query = []
            for query in input.searchOption:
                keywords = [search_format.format(word) for keyword in query.keywords for word in keyword.split(" ")]
                if len(keywords) > 1:
                    keywords = f" {query.operator.upper()} ".join(keywords)
                else:
                    keywords = keywords[0]
                search_query.append({"query_string": {"query": keywords, "fields": query.field}})
                logger.info(search_query)

            # search_query = base_query(len_search, input.searchOption)
            filter_query = base_query(len_filter, input.filterOption)

            # range option
            for query in input.rangeOption:
                filter_query.append(make_format("range", query.field, query.compare_dict))
                logger.info(filter_query)

            body = make_format("query", "bool", {"must": search_query, "filter": filter_query})
            logger.info(body)

        docmanager.set_body(body)
        data = {
            "header": session.get_column_info(input.index, settings.DB_INFO.SCHEMA),
            "count": docmanager.count(body),
            "body": search_filter(docmanager.find(input.resultField)),
        }
        result = {"result": 1, "data": data}
    except Exception as e:
        result = {"result": 0, "errorMessage": str(e)}
        logger.error(e, exc_info=True)
    return result
