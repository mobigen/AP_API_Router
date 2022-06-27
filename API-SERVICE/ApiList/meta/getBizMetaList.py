from lib2to3.pytree import convert
from typing import Dict,List
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, get_token_info, make_res_msg
from fastapi import Query
from fastapi.logger import logger
from starlette.requests import Request


def api(request: Request,
        perPage: int,
        curPage: int,
        keyWordList: List[str] = Query(None)) -> Dict:

    user_info = get_token_info(request.headers)
    curPage = curPage - 1
    v_biz_meta_query = "SELECT kor_nm,eng_nm,nm_id FROM v_biz_meta"
    total_cnt_query = "SELECT count(*) as cnt FROM v_biz_meta_wrap"
    v_meta_wrap_query = """
        select
            *,
            row_number () over (
        order by
            {0}
            ) as rowNo
        from
            meta.v_biz_meta_wrap
    """

    try:
        db = connect_db(config.db_info)
        total_cnt = db.select(total_cnt_query)

        if len(keyWordList):
            order_condition = str()
            search_condition = "data_nm like '%{0}%'"
            v_meta_wrap_query = v_meta_wrap_query + " WHERE "

            # 검색 조건 추가
            for word in keyWordList:
                order_condition = order_condition + f"data_nm similar to '%{word}%' and "
                v_meta_wrap_query = v_meta_wrap_query + search_condition.format(word) + " and "

            # 마지막 ' and ' 삭제
            v_meta_wrap_query = v_meta_wrap_query[:-5]
            v_meta_wrap_query = v_meta_wrap_query.format(order_condition[:-5] + " desc")
        else:
            v_meta_wrap_query = v_meta_wrap_query.format("biz_dataset_id")
        v_meta_wrap_query = v_meta_wrap_query + f" limit {perPage}  offset ({perPage} * {curPage})"

        meta_wrap = db.select(v_meta_wrap_query)
        meta_map = db.select(v_biz_meta_query)
    except Exception as err:
        result = {"result": 0, "errorMessage": err}
        logger.error(err)
    else:
        if len(meta_wrap[0]):
            body = {"totalcount": total_cnt[0][0]['cnt']}
            body["searchList"] = [meta_data for meta_data in meta_wrap[0]]

            result = {"result":1,"errorMessage":"","data":body}
            # result = make_res_msg(1,"",body,"")
        else:
            body = {"totalcount": total_cnt[0][0]['cnt'], "searchList":meta_wrap[0]}
            result = {"result":1,"errorMessage":"","data":body}
            # result = make_res_msg(1,"",meta_wrap[0])

    return result
