from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_exception_info, convert_data
import os
import base64


def print_files_in_dir(root_dir, file_name):
    files = os.listdir(root_dir)
    print(len(files))
    for file in files:
        path = os.path.join(root_dir, file, file_name)
        print(path)


def api() -> Dict:
    eda_path = "/Users/cbc/Downloads/EDA_FILE"
    try:
        db = connect_db()
        files = os.listdir(eda_path)
        id_cnt = 0
        for index, rid in enumerate(files):
            print(index)
            path = os.path.join(eda_path, rid, "profile_report_merged.html")
            with open(path, "rb") as fd:
                data = fd.read()
                data_base64 = base64.b64encode(data).decode("ascii")
                insert_data = f"data:text/html;base64,{data_base64}"
                print(f"LEN : {len(insert_data)}")
                # print(insert_data)
                # query = f'UPDATE meta_temp SET file_data = {convert_data(insert_data)}\
                #            WHERE gimi9_rid = {convert_data(rid)}'
                select_query = f"select biz_dataset_id from meta_temp where gimi9_rid = {convert_data(rid)}"
                select_res, _ = db.select(select_query)
                if select_res:
                    biz_dataset_id = select_res[0]["biz_dataset_id"]
                    query = f"INSERT INTO tb_meta_html (biz_dataset_id, file_data) VALUES ({convert_data(biz_dataset_id)}, {convert_data(insert_data)});"
                    db.execute(query)
                else:
                    id_cnt += 1
            print(f"id_cnt : {id_cnt}")

    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:

        result = {"result": 1, "errorMessage": ""}

    return result
