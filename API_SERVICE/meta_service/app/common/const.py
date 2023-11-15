from pydantic import BaseModel

from libs.database.dml_controller import Base


class Prefix(BaseModel):
    index: str
    size: int
    fields: list
    query: str


class MetaTempTable(Base):
    table_nm = "meta_temp"
    key_column = "gimi9_rid"


class MetaHtmlTable(Base):
    table_nm = "tb_meta_html"
    key_column = "emid"
