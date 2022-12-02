import os
from pathlib import Path
from datetime import datetime
from elasticsearch import helpers
from ELKSearch.Utils.database_utils import prepare_config, connect_db, select, config

root_path = str(Path(os.path.dirname(os.path.abspath(__file__))))
prepare_config(root_path)


def main():
    today = datetime.today().date()
    bulk_meta_item = list()
    prepare_config(root_path)
    es = config.es
    db = connect_db()

    if config.category == "data":
        table_name = "vw_ifs_tbl_txn"
        condition = f"WHERE DATE(tbl_first_cret_dt) > DATE('{today}')" \
                    f"OR DATE(tbl_last_chg_dt) >= DATE('{today}')"
    else:
        table_name = "vw_assets_biz_meta_bas"
        condition = f"WHERE DATE(amd_date) > DATE('{today}')" \
                    f"OR DATE(reg_date) >= DATE('{today}')"

    db_query = f"SELECT * FROM {table_name} "

    if config.check == "True":
        db_query = db_query + condition

    meta_wrap_list = select(db, db_query)[0]

    try:
        for meta_wrap in meta_wrap_list:
            els_dict = dict()
            if config.category != "data":
                if meta_wrap["upd_pam_date"]:
                    meta_wrap["upd_pam_date"] = datetime.strptime(meta_wrap["upd_pam_date"], '%Y-%m-%d')
            els_dict["_id"] = meta_wrap["biz_dataset_id"]
            els_dict["_source"] = meta_wrap
            els_dict["_source"]["biz_dataset_id"] = meta_wrap["biz_dataset_id"]
            # es.insert(meta_wrap,meta_wrap["biz_dataset_id"])
            bulk_meta_item.append(els_dict)
        helpers.bulk(es.conn, bulk_meta_item, index=es.index)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
