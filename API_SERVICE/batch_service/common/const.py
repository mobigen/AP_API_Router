import os
from pydantic import BaseSettings
from batch_service.common.config import base_dir
from libs.database.dml_controller import Base

# log_dir = "{os.path.dirname(base_dir)}/meta_service/log/"
log_dir = f"{os.path.dirname(os.path.dirname(base_dir))}/API-SERVICE/log/meta"

msg_setting = {
    "register": {
        "tmplt": f"{base_dir}/template/emailAthnSend.html",
        "sub": "[자동차데이터포털]회원가입을 위한 인증 메일입니다.",
    },
    "password": {
        "tmplt": f"{base_dir}/template/pwdEmailAthn.html",
        "sub": "[자동차데이터포털]비밀번호 변경을 위한 인증 메일입니다.",
    },
    "share": {
        "tmplt": f"{base_dir}/template/shareEmail.html",
        "sub": "[자동차데이터포털] 자동차데이터포털에서 공유한 데이터입니다.",
    },
    "noty": {
        "tmplt": f"{base_dir}/template/notyEmail.html",
        "sub": "[자동차데이터포털] 자동차데이터포털에서 보내는 알림 메일입니다.",
    },
    "analysisRequest": {
        "tmplt": f"{base_dir}/template/analysisRequestEmail.html",
        "sub": "[자동차데이터포털] {0} 신청 메일입니다.",
    },
    "toolApply": {
        "tmplt": f"{base_dir}/template/toolApplyEmail.html",
        "sub": "[자동차데이터포털] {0} 신청 메일입니다.",
    }
}


class Settings(BaseSettings):
    EMAIL_ADDR: str = ""
    EMAIL_PASSWORD: str = ""
    SMTP_SERVER: str = ""
    SMTP_PORT: str = ""

    class Config:
        env_file = f"{base_dir}/.env"
        env_file_encoding = "utf-8"


class EmailSendInfoTable(Base):
    table_nm = "tb_email_send_info"
    key_column = "email_id"

    def get_query_data(self, st_time) -> dict:
        return {
            "table_nm": self.table_nm,
            "where_info": [
                {
                    "table_nm": self.table_nm,
                    "key": "sttus",
                    "value": "REQ",
                    "compare_op": "=",
                    "op": "",
                },
                {
                    "table_nm": self.table_nm,
                    "key": "reg_date",
                    "value": st_time,
                    "compare_op": ">=",
                    "op": "AND"
                }
            ],
        }


class BizDataTable(Base):
    table_nm = "v_biz_meta_info"
    key_column = "status"


class CkanDataTable(Base):
    table_nm = "v_biz_meta_ckan"
    key_column = "biz_dataset_id"


class RecommendKeyTable(Base):
    table_nm = "tb_recommend_keyword"
    key_column = "keyword"
