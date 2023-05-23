from typing import List, Union
from pydantic import BaseModel, Field, dataclasses


class ElsServerConfig(BaseModel):
    host: str
    port: str


@dataclasses.dataclass
class ElsIndexConfig(BaseModel):
    host: str
    port: str
    index: str


class CoreOption(BaseModel):
    field: Union[list, str]
    keywords: list
    operator: str


class SortOption(BaseModel):
    field: str
    order: str


class InputModel(BaseModel):
    index: str = ""
    from_: int = Field(1, alias="from")
    size: int = 10
    resultField: list = []
    sortOption: List[SortOption] = []
    searchOption: List[CoreOption] = []
    filterOption: List[CoreOption] = []
