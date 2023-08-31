import logging
import smtplib
from datetime import datetime, timedelta

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pydantic import BaseSettings
from batch_service.database.conn import db
from batch_service.common.config import base_dir


logger = logging.getLogger()


class Settings(BaseSettings):
    EMAIL_ADDR: str = ""
    EMAIL_PASSWORD: str = ""
    SMTP_SERVER: str = ""
    SMTP_PORT: str = ""

    class Config:
        env_file = f"{base_dir}/.env"
        env_file_encoding = "utf-8"


def send_email():
    """
    email status의 상태는 REQ, TRY, SEND 3단계
    rgstdt가 1분 이하인 data만 실행
    TRY는 email 전송 단계 이전에 업데이트

    일정 시간 이상 TRY하면 REQ로 변경하여 다시시도 혹은 완전 실패로 변경
    """
    # session = next(db.get_db())
    st_time = datetime.today() - timedelta(minutes=1)
    st_time = st_time.strftime("%Y-%m-%d %H:%M:00")
    table_nm = "email_send_hist"
    data_query = {
        "table_nm": table_nm,
        "key": "*",
        "where_info": [
            {
                "table_nm": table_nm,
                "key": "sttus",
                "value": "REQ,TRY",
                "compare_op": "in",
                "op": ""
            },
            {
                "table_nm": table_nm,
                "key": "trycnt",
                "value": 6,
                "compare_op": "<",
                "op": "AND"
            },
            {
                "table_nm": table_nm,
                "key": "rgstdt",
                "value": st_time,
                "compare_op": ">=",
                "op": "AND"
            }
        ]
    }
    try:
        with db.get_db_manager() as session:
            rows = session.query(**data_query).all()
            rows = rows[0] if rows else []
            logger.info(rows)
            if rows:
                for row in rows:
                    logger.info(row)
                    update_query = {
                        "method": "UPDATE",
                        "table_nm": table_nm,
                        "data": row,
                        "key": ["emid"]
                    }

                    update_query["data"]["sttus"] = "TRY"
                    update_query["data"]["trycnt"] = row["trycnt"] + 1
                    session.execute(**update_query)

                    # send(row)

                    update_query["data"]["sttus"] = "SEND"
                    session.execute(**update_query)

        result = {"result":1,"data": "success"}

    except Exception as e:
        result = {"result": 0, "errorMessage": str(e)}
        logger.error(e, exc_info=True)

    return result


def send(data):
    setting = Settings()
    msg = MIMEMultipart()
    msg["Subject"] = data["title"]

    with open(f"{base_dir}/template/{data['tmpl']}.html","r") as fd:
        html = "\n".join(fd.readlines())

    # cntnt = 사용자 이름|임시비밀번호|발급시간
    content = data["cntnt"].split("|")

    html = html.replace("TITLE", data["title"])
    html = html.replace("USER", content[0])
    html = html.replace("PASSWORD", content[1])
    html = html.replace("REG_DATE", content[2])

    html_part = MIMEText(html, "html")
    msg.attach(html_part)

    with smtplib.SMTP(setting.SMTP_SERVER, int(setting.SMTP_PORT)) as s:
        s.ehlo()
        # s.starttls()
        s.login(setting.EMAIL_ADDR, setting.EMAIL_PASSWORD)
        s.sendmail(setting.EMAIL_ADDR, data["reddr"], msg.as_string())

