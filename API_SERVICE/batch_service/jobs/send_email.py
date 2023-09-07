import logging
import smtplib
from datetime import datetime, timedelta

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from batch_service.database.conn import db
from batch_service.common.const import EmailSendInfoTable, Settings, msg_setting


logger = logging.getLogger()


def send_mail():
    with db.get_db_manager() as session:
        email_send_table = EmailSendInfoTable()
        rows = session.query(**email_send_table.get_query_data()).all()
        rows = rows[0] if rows else []

        for row in rows:

            # send config
            setting = Settings()
            host = setting.SMTP_SERVER
            port = setting.SMTP_PORT
            from_ = setting.EMAIL_ADDR
            password = setting.EMAIL_PASSWORD
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

            if category == "analysisRequest":
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
