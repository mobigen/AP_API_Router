EXCLUDE_HEADERS = ["content-length", "user-agent"]
ROUTE_DATA = """{
    "table_nm": "tb_api_info",
    "key": "ctgry",
    "join_info": {"table_nm": "tb_api_server_info", "key": "ctgry"},
    "where_info": [
        {
            "table_nm": "tb_api_info",
            "key": "route_url",
            "value": "{route_path}",
            "compare_op": "=",
            "op": "",
        },
        {"table_nm": "tb_api_info", "key": "meth", "value": "{method}", "compare_op": "=", "op": "and"},
    ]
}"""
ROUTE_IP_FIELD = "ip_adr"
ROUTE_API_URL_FIELD = "url"
