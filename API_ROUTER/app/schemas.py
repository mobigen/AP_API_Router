from pydantic import BaseModel
from typing import Optional


class ApiServerInfo(BaseModel):
    srvr_nm: str
    ip_adr: str
    domn_nm: Optional[str]


class ApiInfo(BaseModel):
    api_nm: str
    route_url: str
    url: Optional[str]
    mthd: str
    cmd: Optional[str]
    mode: str
    srvr_nm: str
