import logging
import smtplib
from datetime import datetime, timedelta

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from batch_service.app.database.conn import db
from batch_service.app.common.const import EmailSendInfoTable, msg_setting
from batch_service.app.common.config import settings

logger = logging.getLogger()


def send_mail():
    st_time = datetime.today() - timedelta(minutes=1)
    st_time = st_time.strftime("%Y-%m-%d %H:%M:00")

    with db.get_db_manager() as session:
        email_send_table = EmailSendInfoTable()
        rows = session.query(**email_send_table.get_query_data(st_time)).all()
        rows = rows[0] if rows else []

        for row in rows:

            # send config
            host = settings.SMTP_SERVER
            port = settings.SMTP_PORT
            from_ = settings.EMAIL_ADDR
            password = settings.EMAIL_PASSWORD
            category = msg_setting[row["tmplt_cd"]]

            # template
            with open(category["tmplt"],"r") as fp:
                html = "\n".join(fp.readlines())

            # replace
            # todo 함수화
            if row["tmplt_cd"] in ["register","password","share"]:
                html = html.replace("CONTENTS1", row['contents'])
            else:
                content = row["contents"].split("|")
                html = html.replace("TITLE", row['title'])
                html = html.replace("CONTENTS1", content[0])
                html = html.replace("CONTENTS2", content[1])

            if category in ["analysisRequest", "toolApply"]:
                category["sub"] = category["sub"].format(row["title"])

            # send
            message = MIMEMultipart("alternative")
            message["Subject"] = category["sub"]
            message["From"] = from_
            message["To"] = row["rcv_adr"]
            html_part = MIMEText(html, "html")
            message.attach(html_part)

            stmp = smtplib.SMTP(host=host, port=port)
            stmp.ehlo()
            stmp.starttls()
            stmp.login(from_, password)
            stmp.send_message(message)
            stmp.quit()

            # update
            row["sttus"] = "SEND"
            session.execute(**EmailSendInfoTable.get_execute_query("UPDATE", row))
