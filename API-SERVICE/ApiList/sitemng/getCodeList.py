from typing import Dict
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_token_info, make_res_msg
from fastapi.logger import logger
from starlette.requests import Request
from Utils.DataBaseUtil import convert_data


def api(request: Request,
        perPage: int,
        curPage: int,
        gropId: str,
        keyword: str = ""):

    user_info = get_token_info(request.headers)
    curPage = curPage - 1
    total_cnt_query = "SELECT count(*) as cnt FROM tb_code_detail"
    code_list_query = """
        select
            *,
            row_number () over (
        order by
            {0}
            ) as rowNo
        from
            tb_code_detail
    """

    try:
        db = connect_db(config.db_info)

        code_list_query = code_list_query + f" WHERE code_group_id = {convert_data(gropId)}"
        total_cnt_query = total_cnt_query + f" WHERE code_group_id = {convert_data(gropId)}"

        if len(keyword):
            order_condition = f"code_nm similar to '%{keyword}%' "
            search_condition = f"and code_nm like '%{keyword}%'"
            # 검색 조건 추가
            code_list_query = code_list_query + search_condition
            total_cnt_query = total_cnt_query + search_condition

            # 마지막 ' and ' 삭제
            code_list_query = code_list_query.format(
                order_condition + " desc")
        else:
            order_condition = "reg_date asc"
            code_list_query = code_list_query.format(order_condition)

        paging_condition = f" limit {perPage}  offset ({perPage} * {curPage})"
        code_list_query = code_list_query + paging_condition
        logger.info(code_list_query)

        code_list = db.select(code_list_query)
        total_cnt = db.select(total_cnt_query)

    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
        return result
    else:
        if len(code_list[0]):
            result = {"totalcount": total_cnt[0][0]['cnt']}
            result["list"] = [{"code_id": code_detail["code_id"], "code_nm": code_detail["code_nm"]}
                              for code_detail in code_list[0]]
            return result
        else:
            body = {"totalcount": total_cnt[0][0]['cnt'], "list": code_list[0]}
            result = {"result": 1, "errorMessage": "", "data": body}
            return result
