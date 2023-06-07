import logging
import decimal

from fastapi import Depends, APIRouter

from meta_service.database.conn import db
from libs.database.connector import Connector

from meta_service.ELKSearch.config import dev_server
from meta_service.common.search import default_search_set


router = APIRouter()

logger = logging.getLogger()


@router.post("/els-update", response_model=dict)
def els_update(index: str, session: Connector = Depends(db.get_db)):

    # data_query = "SELECT {0} FROM {1};"
    data_query = {"table_nm": index}
    
    try:
        cur = session.conn.cursor()
        column_dict = session.get_column_info(index)
        columns = [col["column_name"] for col in column_dict]
        logger.info(columns)
        rows = session.query(**data_query).all()[0]

        docmanager = default_search_set(dev_server, index)

        insert_dataset = []
        for row in rows:
            insert_body = dict()
            for i in range(0,len(columns)):
                if type(row[columns[i]]) ==decimal.Decimal:
                    insert_body[columns[i]] = int(row[columns[i]])
                else:
                    insert_body[columns[i]] = row[columns[i]]
            docmanager.set_body(insert_body)
            logger.info(docmanager.insert(insert_body["idx"]))
        result = {"result":1,"data": "test"}

    except Exception as e:
        result = {"result": 0, "errorMessage": str(e)}
        logger.error(e, exc_info=True)
    return result