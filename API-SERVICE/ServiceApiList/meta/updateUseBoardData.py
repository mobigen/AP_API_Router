from typing import Dict
from ServiceUtils.CommonUtil import connect_db, get_exception_info, convert_data
from pydantic import BaseModel
from datetime import datetime, timedelta


class updateUseBoardData(BaseModel):
    apyr: str
    use_dataset_id: str
    biz_dataset_id: str
    apy_sbst: str


def api(use_board_data: updateUseBoardData) -> Dict:
    get_biz_meta_query = f'SELECT * FROM v_biz_meta_wrap \
                                    WHERE biz_dataset_id = {convert_data(use_board_data.biz_dataset_id)};'

    try:
        db = connect_db()
        biz_dataset, _ = db.select(get_biz_meta_query)
        biz_dataset = biz_dataset[0]

        use_st_dt = datetime.today().strftime("%Y-%m-%d")
        exp_date = (datetime.today() + timedelta(30)).strftime("%Y-%m-%d")
        trt_sttus = "활용중"
        use_tmscnt = 2
        apy_sbst = use_board_data.apy_sbst

        update_use_data_query = f'UPDATE tb_board_use SET \
                                            data_nm = {convert_data(biz_dataset["data_nm"])},\
                                            ctgry = {convert_data(biz_dataset["ctgry"])},\
                                            file_size = {convert_data(biz_dataset["file_size"])},\
                                            law_evl_conf_yn = {convert_data(biz_dataset["law_evl_conf_yn"])},\
                                            use_st_dt = {convert_data(use_st_dt)},\
                                            exp_date = {convert_data(exp_date)},\
                                            trt_sttus = {convert_data(trt_sttus)},\
                                            use_tmscnt = {convert_data(use_tmscnt)},\
                                            apy_sbst = {convert_data(apy_sbst)}\
                                        WHERE use_dataset_id = {convert_data(use_board_data.use_dataset_id)};'

        db.execute(update_use_data_query)
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = {"result": 1, "errorMessage": ""}

    return result
