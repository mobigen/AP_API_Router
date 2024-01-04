import os

from batch_service.app.common.config import base_dir
from libs.database.dml_controller import Base

# recommend
log_dir = f"{os.path.dirname(os.path.dirname(base_dir))}/API_SERVICE/meta_service/log"

# send_email
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


# els update
class BizDataTable(Base):
    table_nm = "v_biz_meta_info"
    key_column = "status"


class CkanDataTable(Base):
    # 해외데이터
    table_nm = "v_biz_meta_oversea_els"
    key_column = "biz_dataset_id"


# 추천 검색어
class RecommendKeyTable(Base):
    table_nm = "tb_recommend_keyword"
    key_column = "keyword"


# 서울대 데이터
class SeoulDataKor(Base):
    table_nm = "tbdataset_total_95_kor"
    key_column = "ds_id"


class SeoulDataWorld(Base):
    table_nm = "tbdataset_total_95_world"
    key_column = "ds_id"
