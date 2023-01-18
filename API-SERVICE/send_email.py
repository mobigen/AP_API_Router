import os
from email.mime.text import MIMEText
from pathlib import Path

from ELKSearch.Utils.database_utils import connect_db, select, execute, config, prepare_config
from Utils import send_mail

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

    for email_info in send_list:

        try:
            with open(f'{root_path}/conf/sitemng/template/{email_info["tmplt_cd"]}Email.html', "r") as fd:
                html = "\n".join(fd.readlines())

            if email_info["tmplt_cd"] == "share":
                subject = "[자동차데이터포털] 자동차데이터포털에서 공유한 데이터입니다."
                html = html.replace("URL", email_info['contents'])
            else:
                subject = f"[자동차데이터포털] {email_info['title']} 신청 메일 입니다."
                content = email_info["contents"].split("|")
                html = html.replace("TITLE", email_info['title'])
                html = html.replace("CONTENTS1", content[0])
                html = html.replace("CONTENTS2", content[1])

            print(html)
            html_part = MIMEText(html, "html")
            send_mail(html_part, subject=subject, from_=config.els_info["login_user"],
                      to_=email_info['rcv_adr'], config=config.els_info)
        except Exception as e:
            print(e)
        else:
            # update status
            query = f"UPDATE tb_email_send_info SET sttus = 'SEND'" \
                    f"WHERE email_id = '{email_info['email_id']}'"
            execute(db, db.cursor(), query)


if __name__ == "__main__":
    main()
