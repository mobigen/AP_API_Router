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


class CkanDataTable(Base):
    # 해외데이터
    table_nm = "v_biz_meta_oversea_els"
    key_column = "biz_dataset_id"

