from typing import Dict, List
from psycopg2 import pool


class ApiRouteConfig:
    root_path: str

    db_type: str
    db_info: Dict

    remote_info: Dict

    server_host: str
    server_port: int

    api_config: Dict

    api_server_info: List[Dict]
    api_info: List[Dict]
    api_params: List[Dict]

    secret_info: Dict
    lamp_info: Dict
    conn_pool: pool.SimpleConnectionPool


config = ApiRouteConfig
