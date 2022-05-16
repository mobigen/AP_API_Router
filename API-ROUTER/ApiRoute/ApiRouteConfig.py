from typing import Dict, List


class ApiRouteConfig:
    root_path: str

    db_type: str
    db_info: Dict

    remote_info: Dict

    server_host: str
    server_port: int

    api_config: Dict
    api_server_info: List[Dict]


config = ApiRouteConfig
