EXCLUDE_HEADERS = ["content-length", "user-agent"]

ROUTE_IP_FIELD = "ip_adr"
ROUTE_API_URL_FIELD = "url"


class RouteTable:
    """
        각 프로젝트 별 api router 테이블에 맞게 변경 필요
    """
    api_list_table = "tb_api_info"
    api_server_info_table = "tb_api_server_info"
    main_key = "ctgry"
    join_key = "nm"
    url_key = "route_url"
    method_key = "meth"

    @staticmethod
    def get_query_data(route_path, method) -> dict:
        return {
            "table_nm": RouteTable.api_list_table,
            "key": RouteTable.main_key,
            "join_info": {"table_nm": RouteTable.api_server_info_table, "key": RouteTable.join_key},
            "where_info": [
                {
                    "table_nm": RouteTable.api_list_table,
                    "key": RouteTable.url_key,
                    "value": route_path,
                    "compare_op": "=",
                    "op": "",
                },
                {
                    "table_nm": RouteTable.api_list_table,
                    "key": RouteTable.method_key,
                    "value": method,
                    "compare_op": "=",
                    "op": "and",
                },
            ],
        }
