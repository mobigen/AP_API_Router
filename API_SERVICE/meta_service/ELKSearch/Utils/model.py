from pydantic import BaseModel, Field
from typing import List, Union


class ConfigOption(BaseModel):
    field: Union[list, str]
    keywords: list
    operator: str


class SortOption(BaseModel):
    field: str
    order: str


class InputModel(BaseModel):
    chk: bool = False
    u_id: str
    u_role: str = "ROLE_USER"
    index: str = "biz_meta"
    from_: int = Field(1, alias="from")
    size: int = 10
    resultField: list = []
    sortOption: List[SortOption] = []
    searchOption: List[ConfigOption] = []
    filterOption: List[ConfigOption] = []