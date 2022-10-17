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
        for index, rid in enumerate(files):
            print(index)
            path = os.path.join(eda_path, rid, "profile_report_merged.html")
            with open(path, "rb") as fd:
                data = fd.read()
                data_base64 = base64.b64encode(data).decode('ascii')
                insert_data = f'data:text/html;base64,{data_base64}'
                print(f'LEN : {len(insert_data)}')
                # print(insert_data)
                query = f'UPDATE meta_temp SET file_data = {convert_data(insert_data)}\
                            WHERE gimi9_rid = {convert_data(rid)}'
                db.execute(query)

    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:

        result = {"result": 1, "errorMessage": ""}

    return result
