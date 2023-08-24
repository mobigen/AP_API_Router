from email.mime.text import MIMEText

from ApiService.ApiServiceConfig import config
from Utils.CommonUtil import connect_db
from Utils import send_mail


def get_recv_list():
    # batch 1분에 한번씩 email을 전송하고 status를 req에서 send로 변경한다
    query = "SELECT * FROM tb_email_send_info WHERE sttus = 'REQ'"
    db = connect_db()
    send_list, _ = db.select(query)
    return send_list


def email_handler():
    send_list = get_recv_list()
    print(send_list)
    for email_info in send_list:
        try:
            with open(f'{config.root_path}/conf/sitemng/template/{email_info["tmplt_cd"]}Email.html', "r") as fd:
                html = "\n".join(fd.readlines())

            if email_info["tmplt_cd"] == "share":
                subject = "[자동차데이터포털] 자동차데이터포털에서 공유한 데이터입니다."
                html = html.replace("URL", email_info['contents'])
            else:
                if email_info["tmplt_cd"] == "noty":
                    subject = "[자동차데이터포털] 자동차데이터포털에서 보내는 알림입니다."
                else:
                    subject = f"[자동차데이터포털] {email_info['title']} 신청 메일입니다."
                content = email_info["contents"].split("|")
                html = html.replace("TITLE", email_info['title'])
                html = html.replace("CONTENTS1", content[0])
                html = html.replace("CONTENTS2", content[1])

            html_part = MIMEText(html, "html")
            send_mail(html_part, subject=subject, to_=email_info['rcv_adr'])
        except Exception as e:
            print(e)
        else:
            # update status
            query = f"UPDATE tb_email_send_info SET sttus = 'SEND'" \
                    f"WHERE email_id = '{email_info['email_id']}'"
            db = connect_db()
            db.execute(query)
