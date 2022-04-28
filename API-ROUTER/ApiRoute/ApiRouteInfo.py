
from typing import Dict

from typing import Dict, List


class ApiRouteInfo:
    root_path : str
    
    db_type : str
    db_info : Dict
    
    remote_info : Dict
    
    server_host : str
    server_port : int
    
    api_config : Dict
    

config = ApiRouteInfo