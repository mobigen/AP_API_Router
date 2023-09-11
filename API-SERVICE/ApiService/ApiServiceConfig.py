from typing import Dict
from psycopg2 import pool
from passlib.context import CryptContext


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
    pwd_context: CryptContext
    email_auth: Dict

    conn_pool: pool.SimpleConnectionPool

    keycloak_info: Dict


config = ApiServiceConfig
