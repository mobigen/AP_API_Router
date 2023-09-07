from libs.database.dml_controller import Base


NOT_ALLOWED_TABLES = [""]
time_zone = "Asia/Seoul"
auth_no_len = 10
subject_dict = {
        "register": "[자동차데이터포털]회원가입을 위한 인증 메일입니다.",
        "password": "[자동차데이터포털]비밀번호 변경을 위한 인증 메일입니다.",
        "share": "[자동차데이터포털] 자동차데이터포털에서 공유한 데이터입니다."
}


class EmailAuthTable(Base):
    table_nm = "tb_email_athn_info"
    key_column = "email"


# login_service/LoginTable과 같음
class UserInfoTable(Base):
    table_nm = "tb_user_info"
    key_column = "user_id"


class EmailSendInfoTable(Base):
    table_nm = "tb_email_send_info"
    key_column = "email_id"
