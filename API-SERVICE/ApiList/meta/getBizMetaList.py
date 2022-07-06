from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, make_res_msg
from fastapi.logger import logger


def api(perPage: int,
        curPage: int,
        keyword1: str = "",
        keyword2: str = "",
        keyword3: str = ""):

    curPage = curPage - 1
    total_cnt_query = "SELECT count(*) as cnt FROM v_biz_meta_wrap"
    v_meta_wrap_query = "SELECT *, row_number () OVER (ORDER BY {0}) AS rowNo FROM v_biz_meta_wrap"

    try:
        db = connect_db(config.db_info)
        search_word_list = [keyword1, keyword2, keyword3]
        if any(search_word_list):
            order_condition = []
            search_condition = []

            for word in search_word_list:
                order_condition.append(f"data_nm similar to '%{word}%'")
                search_condition.append(f"data_nm like '%{word}%'")

            total_cnt_query = f'{total_cnt_query} WHERE {" and ".join(search_condition)}'
            v_meta_wrap_query = f'{v_meta_wrap_query} WHERE {" and ".join(search_condition)}'

            v_meta_wrap_query = v_meta_wrap_query.format(
                f'{" and ".join(order_condition)} desc')
        else:
            v_meta_wrap_query = v_meta_wrap_query.format("biz_dataset_id")

        v_meta_wrap_query = f"{v_meta_wrap_query} limit {perPage}  offset ({perPage} * {curPage})"

        meta_wrap = db.select(v_meta_wrap_query)
        total_cnt = db.select(total_cnt_query)

    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        search_list = []
        if len(meta_wrap[0]):
            search_list = [meta_data for meta_data in meta_wrap[0]]

        body = {"totalcount": total_cnt[0][0]
                ['cnt'], "searchList": search_list}
        result = {"result": 1, "errorMessage": "", "data": body}

    return result
