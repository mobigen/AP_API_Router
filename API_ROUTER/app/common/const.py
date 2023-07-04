EXCLUDE_HEADERS = ["content-length", "user-agent"]

ROUTE_IP_FIELD = "ip_adr"
ROUTE_API_URL_FIELD = "url"


class RouteTable:
    api_list_table = "api_item_bas"
    api_server_info_table = "api_item_server_dtl"
    main_key = "srvr_nm"
    join_key = "srvr_nm"
    url_key = "route_url"
    method_key = "mthd"

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
