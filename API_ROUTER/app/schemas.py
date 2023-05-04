from pydantic import BaseModel
from typing import Optional


class RouteInfo(BaseModel):
    url: str
    ip_adr: str
