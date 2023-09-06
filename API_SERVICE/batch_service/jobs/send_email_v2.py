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
        rows = session.query(**EmailSendInfoTable.get_select_query("REQ")).all()
        rows = rows[0] if rows else []

        for row in rows:

            # send config
            setting = Settings()
            host = setting.SMTP_SERVER
            port = setting.SMTP_PORT
            from_ = setting.EMAIL_ADDR
            password = setting.EMAIL_PASSWORD
            tmplt = row["tmplt_cd"]

            # replace
            # todo 함수화
            if row["tmplt_cd"] in ["register","password","share"]:
                with open(msg_setting[row[tmplt]]["tmplt"],"r") as fp:
                    html = "\n".join(fp.readlines())
                html = html.replace("CONTENTS1", row['contents'])
            else:
                with open(msg_setting[row[tmplt]]["tmplt"] + "","r") as fp:
                    html = "\n".join(fp.readlines())
                content = row["contents"].split("|")
                html = html.replace("TITLE", row['title'])
                html = html.replace("CONTENTS1", content[0])
                html = html.replace("CONTENTS2", content[1])

            # send
            message = MIMEMultipart("alternative")
            message["Subject"] = msg_setting[row[tmplt]]["sub"]
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
            EmailSendInfoTable.get_execute_query("UPDATE", row)


def send(msg, **kwargs):
    try:
        pass

    except Exception as e:
        raise e