from typing import Dict
from Utils.CommonUtil import connect_db, make_res_msg, get_exception_info
from Utils.DataBaseUtil import convert_data
from io import StringIO
import csv


def csv_to_dict(sample_contents: str):
    sample_contents = sample_contents.replace("\uFEFF", "")
    data_list = []
    with StringIO(sample_contents) as f_sample_contents:
        csvReader = csv.DictReader(f_sample_contents)
        for row in csvReader:
            data_list.append(row)
    return data_list, data_list[0].keys()


def api(datasetId: str = None) -> Dict:
    v_meta_sample_query = f'SELECT * FROM tb_meta_detail_sampledata WHERE biz_dataset_id = {convert_data(datasetId)}'

    try:
        db = connect_db()
        meta_sample, _ = db.select(v_meta_sample_query)
        data_list, column_list = csv_to_dict(meta_sample[0]["sample_contents"])
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = make_res_msg(1, "", data_list, column_list)

    return result
