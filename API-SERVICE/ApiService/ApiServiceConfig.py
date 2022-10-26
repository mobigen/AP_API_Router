from typing import Dict
from psycopg2 import pool


class ApiServiceConfig:
    root_path: str

    category: str

    db_type: str
    db_info: Dict

    remote_info: Dict

    server_host: str
    server_port: int

    api_config: Dict

    secret_info: Dict
    user_info: Dict
    lamp_info: Dict
    conn_pool: pool.SimpleConnectionPool


config = ApiServiceConfig
