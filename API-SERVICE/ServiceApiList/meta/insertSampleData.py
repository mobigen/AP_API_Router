from typing import Dict
from ServiceUtils.CommonUtil import connect_db, get_exception_info, convert_data
from pydantic import BaseModel


class isnertSampleData(BaseModel):
    biz_dataset_id: str
    sample_contents: str
    column_seperator: str = ","
    file_nm: str
    file_extension: str = "csv"


def api(file_path: str, sample_data: isnertSampleData) -> Dict:
    try:
        db = connect_db()
        with open(f'{file_path}/{sample_data.file_nm}.{sample_data.file_extension}', 'r', encoding='cp949') as fp:
            data = fp.read().replace("'", "''").split("\n")
            sample_data.sample_contents = '\n'.join(data)

        insert_sample_query = f'INSERT INTO tb_meta_detail_sampledata(biz_dataset_id, sample_contents, column_seperator, column_count, file_nm, file_extension) \
                                VALUES({convert_data(sample_data.biz_dataset_id)},{convert_data(sample_data.sample_contents)},{convert_data(sample_data.column_seperator)}, \
                                       {convert_data(len(data))},{convert_data(sample_data.file_nm)},{convert_data(sample_data.file_extension)})'
        db.execute(insert_sample_query)

    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = {"result": 1, "errorMessage": ""}
    return result
