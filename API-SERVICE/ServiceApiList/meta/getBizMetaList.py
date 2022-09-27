from typing import Dict
from ServiceUtils.CommonUtil import connect_db, get_exception_info


def api(perPage: int,
        curPage: int,
        keyword1: str = "",
        keyword2: str = "",
        keyword3: str = "") -> Dict:

    curPage = curPage - 1
    total_cnt_query = "SELECT count(*) AS cnt FROM v_biz_meta_wrap"
    v_meta_wrap_query = "SELECT *, row_number () OVER (ORDER BY {0}) AS rowNo FROM v_biz_meta_wrap"

    try:
        db = connect_db()
        search_word_list = [keyword1, keyword2, keyword3]
        if any(search_word_list):
            order_condition = []
            search_condition = []

            for word in search_word_list:
                order_condition.append(f"data_nm SIMILAR to '%{word}%'")
                search_condition.append(f"data_nm LIKE '%{word}%'")

            total_cnt_query = f'{total_cnt_query} WHERE {" AND ".join(search_condition)}'
            v_meta_wrap_query = f'{v_meta_wrap_query} WHERE {" AND ".join(search_condition)}'

            v_meta_wrap_query = v_meta_wrap_query.format(
                f'{" AND ".join(order_condition)} DESC')
        else:
            v_meta_wrap_query = v_meta_wrap_query.format("biz_dataset_id")

        v_meta_wrap_query = f"{v_meta_wrap_query} LIMIT {perPage}  OFFSET ({perPage} * {curPage})"

        meta_wrap = db.select(v_meta_wrap_query)
        total_cnt = db.select(total_cnt_query)

    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        search_list = []
        if len(meta_wrap[0]):
            search_list = [meta_data for meta_data in meta_wrap[0]]

        body = {"totalcount": total_cnt[0][0]
                ['cnt'], "searchList": search_list}
        result = {"result": 1, "errorMessage": "", "data": body}

    return result
