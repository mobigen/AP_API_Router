import decimal
import logging
import os.path

from fastapi import Depends, APIRouter
from pydantic import BaseModel

from libs.database.connector import Executor
from libs.els.ELKSearch.Utils.base import make_format
from libs.els.ELKSearch.Utils.base import set_els
from libs.els.ELKSearch.Utils.document_utils import search_filter
from libs.els.ELKSearch.index import Index
from meta_service.app.common.config import settings
from meta_service.app.common.const import Prefix
from meta_service.app.common.search import SearchModel
from meta_service.app.common.search import default_search_set, base_query, record_keyword, search_count, Record
from meta_service.app.common.utils import data_process
from meta_service.app.database.conn import db

router = APIRouter()

logger = logging.getLogger()


class Record(BaseModel):
    biz_dataset_id: str


@router.post("/bulk_update", response_model=dict)
def els_update(index: str, key: str = "biz_dataset_id", session: Executor = Depends(db.get_db)):
    """
    - bulk update에 사용되는 api X

    :param index: els index 명
    :param key: id 값
    :param session: db session
    :return:
    """
    # data_query = "SELECT {0} FROM {1};"
    data_query = {"table_nm": index}
    try:
        column_dict = session.get_column_info(index, settings.DB_INFO.SCHEMA)
        columns = [col["column_name"] for col in column_dict]
        rows = session.query(**data_query).all()[0]

        docmanager = default_search_set(settings.ELS_INFO.ELS_HOST, settings.ELS_INFO.ELS_PORT, index)

        for row in rows:
            insert_body = dict()
            for i in range(0, len(columns)):
                insert_body[columns[i]] = row[columns[i]]
            insert_body = data_process(insert_body)
            docmanager.set_body(insert_body["_source"])
            logger.info(docmanager.insert(insert_body["_source"][key]))
        result = {"result": 1, "data": "test"}

    except Exception as e:
        result = {"result": 0, "errorMessage": str(e)}
        logger.error(e, exc_info=True)
    return result


@router.post("/getElsBizMetaList")
@router.post("/getElsCkanList")
def search(input: SearchModel):
    """
    :param input:
    {
        "chk": true,
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

        if input.chk and len_search:
            # 추천검색어를 위한 검색어 저장
            record_keyword(input.searchOption)

        # from_ 0 부터 시작해야함, web에서는 1부터 넘어오기 때문에 1을 빼준다
        print(input.dict())
        docmanager = default_search_set(
            settings.ELS_INFO.ELS_HOST, settings.ELS_INFO.ELS_PORT, input.index, input.size, input.from_ - 1
        )

        # query에 조건이 없으면 match all 실행
        if not any([len_filter, len_search, len_range]):
            body = make_format("query", "match_all", dict())
            filter_query = []
        else:
            search_format = "(*{0}*)"
            search_query = []
            for query in input.searchOption:
                keywords = [search_format.format(keyword) for keyword in query.keywords]
                if len(keywords) > 1:
                    keywords = f" {query.operator.upper()} ".join(keywords)
                else:
                    keywords = keywords[0]
                search_query.append(
                    {"query_string": {"query": keywords, "fields": query.field, "minimum_should_match": "100%"}}
                )

            filter_query = base_query(len_filter, input.filterOption)

            # range option
            for query in input.rangeOption:
                filter_query.append(make_format("range", query.field, query.compare_dict))

            body = make_format("query", "bool", {"must": search_query, "filter": filter_query})

        docmanager.set_sort(input.sortOption)
        docmanager.set_body(body)

        data_dict = {"searchList": search_filter(docmanager.find(input.resultField))}
        data_dict.update(search_count(docmanager, filter_query, body))

        result = {"result": 1, "errorMessage": "", "data": data_dict}
    except Exception as e:
        result = {"result": 0, "errorMessage": str(e)}
        logger.error(e, exc_info=True)
    return result


@router.post("/deleteElsBizMeta")
def els_delete(input: Record):
    try:
        pk_key = "biz_dataset_id"
        docmanager = default_search_set(settings.ELS_INFO.ELS_HOST, settings.ELS_INFO.ELS_PORT, index)
        docmanager.delete(pk_key, input.biz_dataset_id)

        result = {"result": 1, "data": f"{input.biz_dataset_id} delete"}
    except Exception as e:
        result = {"result": 0, "errorMessage": str(e)}
        logger.error(e, exc_info=True)
    return result


@router.post("/updateElsBizMeta", response_model=dict)
def els_doc_update(input: Record):
    try:
        index = "biz_meta"
        docmanager = default_search_set(settings.ELS_INFO.ELS_HOST, settings.ELS_INFO.ELS_PORT, index)
        docmanager.update(input.biz_dataset_id)

        result = {"result": 1, "data": f"{input.biz_dataset_id} update"}
    except Exception as e:
        result = {"result": 0, "errorMessage": str(e)}
        logger.error(e, exc_info=True)
    return result


@router.post("/els-index-create", response_model=dict)
def els_index_update(index: str):
    try:
        es = set_els(settings.ELS_INFO.ELS_HOST, settings.ELS_INFO.ELS_PORT)
        ind_manager = Index(es)
        indices = ind_manager.all_index().keys()
        if index not in indices:
            logger.info(
                ind_manager.create(
                    index=index, path=os.path.join(settings.BASE_DIR, "resources", "mapping", f"{index}.json")
                )
            )
        result = {"result": 1, "data": "success"}

    except Exception as e:
        result = {"result": 0, "errorMessage": str(e)}
        logger.error(e, exc_info=True)
    return result


@router.get("/updateElsBizMetaBulk", response_model=dict)
def els_update(session: Executor = Depends(db.get_db)):
    key = "biz_dataset_id"
    table_nm = "v_biz_meta_info"
    index = "biz_meta"
    data_query = {
        "table_nm": table_nm,
        "where_info": [{"table_nm": table_nm, "key": "status", "value": "D", "compare_op": "=", "op": ""}],
    }

    try:
        rows, _ = session.query(**data_query).all()
        print(rows[0])
        columns = list(rows[0].keys())
        print(columns)

        docmanager = default_search_set(settings.ELS_INFO.ELS_HOST, settings.ELS_INFO.ELS_PORT, index)

        for row in rows:
            insert_body = data_process(row)
            print(insert_body)
            docmanager.set_body(insert_body["_source"])
            res = docmanager.insert(insert_body["_id"])
            logger.info(res)
        result = {"result": 1, "data": "test"}

    except Exception as e:
        result = {"result": 0, "errorMessage": str(e)}
        logger.error(e, exc_info=True)
    return result


@router.post("/insertElsBizMeta", response_model=dict)
def els_update(input: Record, session: Executor = Depends(db.get_db)):

    data_query = {
        "table_nm": input.index,
        "where_info": [{"table_nm": input.index, "key": input.key, "value": input.ids, "compare_op": "in", "op": ""}],
    }
    logger.info(data_query)
    try:
        rows, _ = session.query(**data_query).all()
        print(rows[0])
        columns = list(rows[0].keys())
        print(columns)

        docmanager = default_search_set(settings.ELS_INFO.ELS_HOST, settings.ELS_INFO.ELS_PORT, input.index)

        for row in rows:
            for k, v in row.items():
                if isinstance(v, decimal.Decimal):
                    row[k] = int(v)

            # insert_body = exception_col(input.index, insert_body)
            docmanager.set_body(row)
            doc_id = row[input.key]
            logger.info(docmanager.update(doc_id))
        result = {"result": 1, "data": "test"}

    except Exception as e:
        result = {"result": 0, "errorMessage": str(e)}
        logger.error(e, exc_info=True)
    return result


@router.post("/getPrefixBizMeta", response_model=dict)
def autocomplete(input: Prefix):
    """
    자동완성 API
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
        docmanager = default_search_set(settings.ELS_INFO.ELS_HOST, settings.ELS_INFO.ELS_PORT, input.index, input.size)
        input.query = f"(*{input.query}*)"
        del input.index
        del input.size

        search_query = {"query_string": input.dict()}

        body = {"query": {"bool": {"must": [search_query]}}}

        logger.info(body)
        docmanager.set_body(body)
        prefix_dict = search_filter(docmanager.find(input.fields))
        print(prefix_dict)

        if not len(prefix_dict):
            return {"result": 1, "data": []}

        # lower() 대소문자 구별 없이 검색하기 위한 방법
        prefix_data = [
            word for data in prefix_dict for word in data.values() if word and keyword.lower() in word.lower()
        ]

        # 데이터셋에서 해당 되는 데이터가 여러개 있을 수 있어 prefix_data에 size를 줌
        result = {"result": 1, "data": prefix_data[: docmanager.size]}
    except Exception as e:
        result = {"result": 0, "errorMessage": str(e)}
        logger.error(e, exc_info=True)

    return result
