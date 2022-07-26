from typing import Dict, List, Optional
from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db, make_res_msg, get_exception_info
from Utils.DataBaseUtil import convert_data
from pydantic import BaseModel
from fastapi.logger import logger


class joinInfo(BaseModel):
    table_nm: str
    key: str


class whereInfo(BaseModel):
    table_nm: str
    key: str
    value: str
    compare_op: str
    op: Optional[str] = ""


class orderInfo(BaseModel):
    table_nm: str
    key: str
    order: str


class pageInfo(BaseModel):
    per_page: int
    cur_page: int


class commonMatchSelect(BaseModel):
    table_nm: str
    key: Optional[str] = None
    join_info: Optional[joinInfo] = None
    where_info: Optional[List[whereInfo]] = None
    order_info: Optional[orderInfo] = None
    page_info: Optional[pageInfo] = None


def convert_compare_op(compare_str):
    if compare_str == "Equal":
        compare_op = "="
    elif compare_str == "Not Equal":
        compare_op = "!="
    elif compare_str == "Greater Than":
        compare_op = ">"
    elif compare_str == "Greater Than or Equal":
        compare_op = ">="
    elif compare_str == "Less Than":
        compare_op = "<"
    elif compare_str == "Less Than or Equal":
        compare_op = "<="
    else:
        compare_op = compare_str
    return compare_op


def make_select_query(select_info: commonMatchSelect):
    join, where, order, page = "", "", "", ""
    join_info, where_info, order_info, page_info = select_info.join_info, select_info.where_info, select_info.order_info, select_info.page_info
    if join_info:
        join = f'JOIN {join_info.table_nm} ON {select_info.table_nm}.{select_info.key} = {join_info.table_nm}.{join_info.key}'
    if where_info:
        where = "WHERE "
        for info in where_info:
            if info.compare_op == "IN" or info.compare_op == "NOT IN":
                value_list = ", ".join(
                    map(convert_data, info.value.split(",")))
                value = f'( {value_list} )'
            else:
                value = convert_data(info.value)
            where = f'{where} {info.op} {info.table_nm}.{info.key} {convert_compare_op(info.compare_op)} {value}'
    if order_info:
        order = f'ORDER BY {order_info.table_nm}.{order_info.key} {order_info.order}'
    if page_info:
        page = f'LIMIT {page_info.per_page} OFFSET ({page_info.per_page} * {page_info.cur_page - 1})'
    query = f'SELECT * FROM {select_info.table_nm} {join} {where} {order} {page};'
    return query


def api(select_info: commonMatchSelect) -> Dict:
    get_column_info = f"SELECT eng_nm, kor_nm FROM tb_table_column_info \
                                              WHERE table_id = (SELECT id FROM tb_table_list WHERE table_nm = {convert_data(select_info.table_nm)});"
    get_query = make_select_query(select_info)
    logger.info(f'Get Query : {get_query}')

    try:
        db = connect_db(config.db_info)
        select_data, _ = db.select(get_query)
        if select_info.page_info:
            total_cnt_query = f"SELECT count(*) AS totalCount FROM {select_info.table_nm};"
            total_cnt = db.select(total_cnt_query)

    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        column_info, _ = db.select(get_column_info)
        kor_nm_list = [map_data["kor_nm"] for map_data in column_info]
        eng_nm_list = [map_data["eng_nm"] for map_data in column_info]
        result = make_res_msg(1, "", select_data, eng_nm_list, kor_nm_list)
        if select_info.page_info:
            result["data"].update(total_cnt[0][0])
    return result
