from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_exception_info
from fastapi.logger import logger
from Utils.DataBaseUtil import convert_data


def api(perPage: int,
        curPage: int,
        gropId: str,
        keyword: str = "") -> Dict:

    curPage = curPage - 1
    total_cnt_query = "SELECT count(*) AS cnt FROM tb_code_detail"
    code_list_query = "SELECT *, row_number () OVER (ORDER BY {0}) AS rowNo FROM tb_code_detail"

    try:
        db = connect_db()
        common_condition = f" WHERE code_group_id = {convert_data(gropId)}"
        code_list_query = code_list_query + common_condition
        total_cnt_query = total_cnt_query + common_condition

        if len(keyword):
            # keyword 검색 조건 추가
            order_condition = f"code_nm SIMILAR to '%{keyword}%' DESC"
            search_condition = f"AND code_nm LIKE '%{keyword}%'"

            code_list_query = code_list_query + search_condition
            total_cnt_query = total_cnt_query + search_condition
            code_list_query = code_list_query.format(order_condition)
        else:
            order_condition = "reg_date ASC"
            code_list_query = code_list_query.format(order_condition)

        paging_condition = f" LIMIT {perPage}  OFFSET ({perPage} * {curPage})"
        code_list_query = code_list_query + paging_condition

        code_list = db.select(code_list_query)
        total_cnt = db.select(total_cnt_query)

    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        code_info = []
        if len(code_list[0]):
            code_info = [{"code_id": code_detail["code_id"], "code_nm": code_detail["code_nm"]}
                         for code_detail in code_list[0]]

        body = {"totalcount": total_cnt[0][0]['cnt'], "list": code_info}
        result = {"result": 1, "errorMessage": "", "data": body}
        return result
