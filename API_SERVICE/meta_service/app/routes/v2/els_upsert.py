import decimal
import logging

from fastapi import Depends, APIRouter
from meta_service.app.ELKSearch.config import dev_server
from meta_service.app.common.config import settings
from meta_service.app.common.search import default_search_set, Upsert, exception_col
from meta_service.app.database.conn import db

from libs.database.connector import Connector

router = APIRouter()

logger = logging.getLogger()


@router.post("/els-upsert", response_model=dict)
def els_update(input: Upsert, session: Connector = Depends(db.get_db)):

    data_query = {
        "table_nm": input.index,
        "where_info": [{"table_nm": input.index, "key": input.key, "value": input.ids, "compare_op": "in", "op": ""}],
    }
    logger.info(data_query)
    try:
        cur = session.conn.cursor()
        column_dict = session.get_column_info(input.index, settings.DB_INFO.SCHEMA)
        columns = [col["column_name"] for col in column_dict]

        rows = session.query(**data_query).all()[0]
        docmanager = default_search_set(dev_server, input.index)

        insert_dataset = []
        for row in rows:
            insert_body = dict()
            for i in range(0, len(columns)):
                if type(row[columns[i]]) == decimal.Decimal:
                    insert_body[columns[i]] = int(row[columns[i]])
                else:
                    insert_body[columns[i]] = row[columns[i]]

            insert_body = exception_col(input.index, insert_body)
            docmanager.set_body(insert_body)
            doc_id = insert_body[input.key]
            logger.info(docmanager.update(doc_id))
        result = {"result": 1, "data": "test"}

    except Exception as e:
        result = {"result": 0, "errorMessage": str(e)}
        logger.error(e, exc_info=True)
    return result
