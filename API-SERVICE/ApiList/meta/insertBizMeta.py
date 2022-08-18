import uuid
from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_exception_info
from Utils.DataBaseUtil import convert_data


def api(biz_meta_list: list) -> Dict:
    # todo: 수정 필요 (insertMetaMap에서 item_id부여 후 web에서 맞춘다음에 api로 넘겨줘야함)
    # item_id를 web에서 넘겨 받아야 하는 형태
    uid = uuid.uuid4()
    biz_meta_query = 'SELECT item_id as itemId, item_val as itemVal FROM tb_biz_meta;'

    try:
        db = connect_db()
        for biz_meta in biz_meta_list:
            item_id, item_val = tuple(biz_meta.values())
            query = f'INSERT INTO tb_biz_meta (biz_dataset_id, item_id, item_val ) \
                             VALUES ({convert_data(uid)},{convert_data(item_id)},{convert_data(item_val)});'

            db.execute(query)

        biz_meta_list = db.select(biz_meta_query)[0]
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = biz_meta_list
    return result
