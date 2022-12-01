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
    query = "SELECT * FROM email_dsp_hst WHERE sttus = 'REQ'"
    db = connect_db()
    send_list = select(db,query)[0]

    from_addr = config.els_info["from_addr"]
    host = config.els_info["host"]
    port = config.els_info["port"]

    for email_info in send_list:
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = email_info['title']
            message["From"] = from_addr
            message["To"] = email_info['rcv_adr']

            with open(f'{config.root_path}/ELKSearch/conf/template/exTemplate.html', "r") as fd:
                html = "\n".join(fd.readlines())

            html = html.replace("TITLE", email_info['title'])
            html = html.replace("SBST", email_info['sbst'])
            html_part = MIMEText(html, "html")
            message.attach(html_part)

            with smtplib.SMTP(host, port) as smtp:
                # smtp.sendmail(from_addr,email_info['rcv_adr'],message)
                smtp.send_message(message)
        except Exception as e:
            print(0)
            print(e)
        else:
            # update status
            print(1)
            query = f"UPDATE email_dsp_hst SET sttus = 'SEND'" \
                    f"WHERE email_id = '{email_info['email_id']}'"
            execute(db,db.cursor(),query)
        break


if __name__ == "__main__":
    main()
