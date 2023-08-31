from common_libs.libs.database.dml_controller import Base


NOT_ALLOWED_TABLES = ["USR_MGMT"]
INSERT_NOT_ALLOWED_TABLES = [""]
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
EXPIRE_DELTA = 1
COOKIE_NAME = "user-docean-access-token"


class EmailInfoTable(Base):
    table_nm = ""
    key_column = ""


