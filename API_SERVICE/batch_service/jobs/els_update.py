import os
import re
from pathlib import Path
from datetime import datetime
from elasticsearch import helpers
from ELKSearch.Utils.database_utils import prepare_config, connect_db, select, config
from ELKSearch.Utils.elasticsearch_utils import data_process, default_process

root_path = str(Path(os.path.dirname(os.path.abspath(__file__))))
prepare_config(root_path)


def insert_meta(db, es):
    bulk_meta_item = list()
    db_query = f"SELECT * FROM v_biz_meta_info  WHERE status = 'D'"
    if config.check == "True":
        today = datetime.today().date()
        condition = f"AND (DATE(amd_date) >= DATE('{today}')" \
                    f"OR DATE(reg_date) >= DATE('{today}'))"
        db_query = db_query + condition

    meta_wrap_list = select(db, db_query)[0]

    try:
        for meta_wrap in meta_wrap_list:
            els_dict = data_process(meta_wrap)
            bulk_meta_item.append(els_dict)
        helpers.bulk(es.conn, bulk_meta_item, index=es.index)
    except Exception as e:
        print(e)


def insert_ckan(db, es):
    bulk_meta_item = list()
    db_query = "SELECT biz_dataset_id, data_nm, data_desc, notes, reg_date, tags, updt_dt" \
               " FROM v_biz_meta_ckan"

    if config.check == "True":
        today = datetime.today().date()
        condition = f"WHERE (DATE(updt_dt) >= DATE('{today}')" \
                    f"OR DATE(reg_date) >= DATE('{today}'))"
        db_query = db_query + condition

    ckan_wrap_list = select(db, db_query)[0]
    try:
        for ckan in ckan_wrap_list:
            els_dict = default_process(dict(), ckan)
            bulk_meta_item.append(els_dict)
        helpers.bulk(es.conn, bulk_meta_item, index=es.index)
    except Exception as e:
        print(e)


def main():
    """
    :param
    config dir path: {project_path}/ELKSearch/config
        --category=ckan|meta, elasticsearch config
        --db_type=test|commercial , database config
        --check=True|False, True=today False=All
    :return:
    """
    prepare_config(root_path)
    es = config.es
    db = connect_db()

    if config.category == "meta":
        insert_meta(db, es)
    else:
        insert_ckan(db, es)


if __name__ == "__main__":
    main()
