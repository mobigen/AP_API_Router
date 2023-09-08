from pydantic import BaseModel

from ApiService.ApiServiceConfig import config
from Utils import insert_mail_history
from Utils.CommonUtil import send_template_mail, get_exception_info


class EmailInfo(BaseModel):
    email: str
    msg_type: str  # share
    message: str


def api(params: EmailInfo):
    try:
        send_template_mail(params.message, params.email, params.msg_type)
        insert_mail_history(
            rcv_adr=params.email,
            title=config.email_auth[f"subject_{params.msg_type}"],
            contents=params.message,
            tmplt_cd=params.msg_type,
        )

        return {"result": 1, "errorMessage": ""}
    except Exception:
        except_name = get_exception_info()
        return {"result": 0, "errorMessage": except_name}
