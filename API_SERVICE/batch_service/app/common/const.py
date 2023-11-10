import os

from batch_service.app.common.config import base_dir
from libs.database.dml_controller import Base

log_dir = f"{os.path.dirname(os.path.dirname(base_dir))}/API-SERVICE/log/meta"

template_dir = os.path.join(base_dir, "resources", "template")
msg_setting = {
    "register": {
        "tmplt": os.path.join(template_dir, "emailAthnSend.html"),
        "sub": "[자동차데이터포털]회원가입을 위한 인증 메일입니다.",
    },
    "password": {
        "tmplt": os.path.join(template_dir, "pwdEmailAthn.html"),
        "sub": "[자동차데이터포털]비밀번호 변경을 위한 인증 메일입니다.",
    },
    "share": {
        "tmplt": os.path.join(template_dir, "shareEmail.html"),
        "sub": "[자동차데이터포털] 자동차데이터포털에서 공유한 데이터입니다.",
    },
    "noty": {
        "tmplt": os.path.join(template_dir, "notyEmail.html"),
        "sub": "[자동차데이터포털] 자동차데이터포털에서 보내는 알림 메일입니다.",
    },
    "analysisRequest": {
        "tmplt": os.path.join(template_dir, "analysisRequestEmail.html"),
        "sub": "[자동차데이터포털] {0} 신청 메일입니다.",
    },
    "toolApply": {
        "tmplt": os.path.join(template_dir, "toolApplyEmail.html"),
        "sub": "[자동차데이터포털] {0} 신청 메일입니다.",
    },
}


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
                {"table_nm": self.table_nm, "key": "reg_date", "value": st_time, "compare_op": ">=", "op": "AND"},
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


class DatasetDomesticTable(Base):
    table_nm = "tbdataset_domestic_recommendation"
    key_column = "ds_id"


class ResourceReportTable(Base):
    table_nm = "tbresource_report"
    key_column = "rp_id"
