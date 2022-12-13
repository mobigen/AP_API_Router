import os
import smtplib
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ELKSearch.Utils.database_utils import prepare_config, connect_db, select, execute, config

root_path = str(Path(os.path.dirname(os.path.abspath(__file__))))
prepare_config(root_path)


def main():
    """
    :argument
    category = email
    db_type = email_db
    """

    # batch 1분에 한번씩 email을 전송하고 status를 req에서 send로 변경한다
    query = "SELECT * FROM tb_email_send_info WHERE sttus = 'REQ'"
    db = connect_db()
    send_list = select(db, query)[0]

    from_addr = "admin@bigdata-car.kr"
    host = config.els_info["host"]
    port = config.els_info["port"]

    for email_info in send_list:

        try:
            if email_info["tmplt_cd"] == "share":
                share_chk = 1
                subject = "[자동차데이터포털] 자동차데이터포털에서 공유한 데이터입니다."
            else:
                share_chk = 0
                subject = f"[자동차데이터포털] {email_info['title']} 신청 메일 입니다."
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = from_addr
            message["To"] = email_info['rcv_adr']

            with open(f'{config.root_path}/conf/sitemng/template/{email_info["tmplt_cd"]}Email.html', "r") as fd:
                html = "\n".join(fd.readlines())

            if share_chk:
                html = html.replace("URL", email_info['contents'])
            else:
                content = email_info["contents"].split("|")
                html = html.replace("TITLE", email_info['title'])
                html = html.replace("CONTENTS1", content[0])
                html = html.replace("CONTENTS2", content[1])

            html_part = MIMEText(html, "html")
            message.attach(html_part)

            # with smtplib.SMTP(host, port) as smtp:
            with smtplib.SMTP(host,port) as smtp:
                smtp.login(from_addr,config.els_info["index"])
                smtp.send_message(message)
        except Exception as e:
            print(e)
        else:
            # update status
            query = f"UPDATE tb_email_send_info SET sttus = 'SEND'" \
                    f"WHERE email_id = '{email_info['email_id']}'"
            execute(db,db.cursor(),query)


if __name__ == "__main__":
    main()
