from common_libs.libs.database.dml_controller import Base


NOT_ALLOWED_TABLES = [""]
time_zone = "Asia/Seoul"
auth_no_len = 10


class EmailAuthTable(Base):
    table_nm = "tb_email_athn_info"
    key_column = "email"


# login_service/LoginTable과 같음
class UserInfoTable(Base):
    table_nm = "tb_user_info"
    key_column = "user_id"
