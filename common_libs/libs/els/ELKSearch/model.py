from typing import List, Union

from pydantic import BaseModel, Field


class ElkIndexConfig(BaseModel):
    host: str
    port: str
    index: str


class CoreOption(BaseModel):
    field: Union[list, str]
    keywords: Union[list, str]
    operator: str


class SortOption(BaseModel):
    field: str
    order: str


class RangeOption(BaseModel):
    field: str
    compare_dict: dict


class InputModel(BaseModel):
    index: str = ""
    from_: int = Field(1, alias="from")
    size: int = 10
    resultField: list = []
    sortOption: List[SortOption] = []
    searchOption: List[CoreOption] = []
    filterOption: List[CoreOption] = []
    rangeOption: List[RangeOption] = []
