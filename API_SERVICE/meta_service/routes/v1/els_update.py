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
def els_update(session: Connector = Depends(db.get_db)):
    index = "vw_co_if"

    data_query = "SELECT {0} FROM VW_CO_IF;"
    col_query = "SELECT column_name FROM all_tab_columns WHERE table_name = 'VW_CO_IF';"
    try:
        cur = session.conn.cursor()
        cur.execute(col_query)
        # columns ['IDX', 'CONM', 'DFNMTRAIDX', 'BZRGSTCD', 'PRCCTCD',
        # 'COCTIDX', 'PSNIDX', 'PSNNM', 'PHONN', 'OFFRDT', 'ENDDT',
        # 'MDFCDT', 'IFOFFRYN', 'SALPRC', 'SYSTDVL', 'CORETC', 'NRTOFFR', 'COCT', 'DFNMTRA']
        columns = [col_nm[0] for col_nm in cur.fetchall()]

        data_query = data_query.format(",".join(columns))
        cur.execute(data_query)

        docmanager = default_search_set(dev_server, index)

        # insert_dataset = []
        for row in cur.fetchall():
            insert_body = dict()
            for i in range(0,len(columns)):
                col = columns[i].lower()
                if type(row[i]) == decimal.Decimal:
                    insert_body[col] = int(row[i])
                else:
                    insert_body[col] = row[i]

            docmanager.set_body(insert_body)
            logger.info(docmanager.insert(insert_body["idx"]))
        #     insert_dataset.append(insert_body)
        # logger.info(len(insert_dataset))
        result = {"result":1,"data": "test"}

    except Exception as e:
        result = {"result": 0, "errorMessage": str(e)}
        logger.error(e, exc_info=True)
    return result