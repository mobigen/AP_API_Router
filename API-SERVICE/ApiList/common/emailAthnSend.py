from typing import Dict
from fastapi.logger import logger
from pydantic import BaseModel
import smtplib
import string
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from Utils.CommonUtil import get_exception_info, connect_db, convert_data
from ApiService.ApiServiceConfig import config


class emailAthnSend(BaseModel):
    email: str


def make_auth_no():
    string_pool = string.ascii_letters + string.digits
    auth_no = ""
    for _ in range(int(config.email_auth["auth_no_len"])):
        auth_no += random.choice(string_pool)
    return auth_no


def make_email_auth_query(email, auth_no, exist_mail):
    if exist_mail:
        query = f"UPDATE tb_email_athn_info \
                    SET athn_no={convert_data(auth_no)}, send_date=NOW() WHERE email={convert_data(email)};"
    else:
        query = f"INSERT INTO tb_email_athn_info (email, athn_no, athn_yn, send_date) \
                        VALUES ({convert_data(email)}, {convert_data(auth_no)}, 'N', NOW());"
    return query


def send_mail(auth_no, receiver_addr):
    message = MIMEMultipart("alternative")
    message["Subject"] = config.email_auth["subject"]
    message["From"] = config.email_auth["login_user"]
    message["To"] = receiver_addr

    with open(f'{config.root_path}/conf/common/template/emailAthnSend.html', "r") as fd:
        html = "\n".join(fd.readlines())

    html = html.replace("AUTH_NO", auth_no)
    html_part = MIMEText(html, "html")
    message.attach(html_part)

    stmp = smtplib.SMTP(
        host=config.email_auth["server_addr"], port=int(config.email_auth["port"]))
    stmp.ehlo()
    stmp.starttls()
    stmp.login(config.email_auth["login_user"],
               config.email_auth["login_pass"])
    stmp.sendmail(config.email_auth["login_user"],
                  receiver_addr, message.as_string())
    stmp.quit()


def api(email_auth: emailAthnSend) -> Dict:
    try:
        auth_no = make_auth_no()
        db = connect_db()
        exist_mail, _ = db.select(
            f'SELECT * FROM tb_email_athn_info WHERE email={convert_data(email_auth.email)}')

        time_zone = 'Asia/Seoul'
        db.execute(f"SET TIMEZONE={convert_data(time_zone)}")
        query = make_email_auth_query(email_auth.email, auth_no, exist_mail)
        db.execute(query)

        send_mail(auth_no, email_auth.email)
        logger.info("Successfully sent the mail.")
    except Exception:
        except_name = get_exception_info()
        result = {"result": 0, "errorMessage": except_name}
    else:
        result = {"result": 1, "errorMessage": ""}

    return result
