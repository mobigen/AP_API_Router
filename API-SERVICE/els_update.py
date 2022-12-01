import os
import re
from pathlib import Path
from datetime import datetime
from elasticsearch import helpers
from ELKSearch.Utils.database_utils import prepare_config, connect_db, select, config
from ELKSearch.Utils.elasticsearch_utils import data_process

root_path = str(Path(os.path.dirname(os.path.abspath(__file__))))
prepare_config(root_path)


def main():
    bulk_meta_item = list()
    prepare_config(root_path)
    es = config.es
    db = connect_db()

    db_query = f"SELECT * FROM v_biz_meta_info  WHERE status = 'D'"
    if config.check == "True":
        today = datetime.today().date()
        condition = f"AND (DATE(amd_date) >= DATE('{today}')" \
                    f"OR DATE(reg_date) >= DATE('{today}'))"
        db_query = db_query + condition

    meta_wrap_list = select(db,db_query)[0]

    try:
        for meta_wrap in meta_wrap_list:
            els_dict = data_process(meta_wrap)
            bulk_meta_item.append(els_dict)
        helpers.bulk(es.conn, bulk_meta_item, index=es.index)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
