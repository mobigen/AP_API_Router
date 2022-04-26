from pydantic import BaseModel
from typing import Dict, List

class TEST(BaseModel):
    api_name: str
    category: str
    url: str
    msg_type: str
    method: str
    protocol: str
    command: str
    bypass: str
    params: List[Dict]