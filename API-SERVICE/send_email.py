import os
import smtplib
from pathlib import Path
from ELKSearch.Utils.database_utils import prepare_config, connect_db, select, execute

root_path = str(Path(os.path.dirname(os.path.abspath(__file__))))
prepare_config(root_path)


def main():
    # batch 1분에 한번씩 status를 req에서 send로 변경해준다
    from_addr = "DataOcean@kt.com"
    host = "14.63.245.51"
    port = 25
    query = "SELECT * FROM email_dsp_hst WHERE sttus = 'REQ'"
    db = connect_db()
    send_list = select(db,query)[0]

    for email_info in send_list:
        try:
            msg = (
                f"subject: {email_info['title']}\n"
                f"from: {from_addr}\n"
                f"to: {email_info['rcv_adr']}\n"
                f"{email_info['sbst']}\n"
            )
            with smtplib.SMTP(host, port) as smtp:
                smtp.sendmail(from_addr,email_info['rcv_adr'],msg)
        except Exception as e:
            print(e)
        else:
            # update status
            query = f"UPDATE email_dsp_hst SET sttus = 'SEND'"\
                    f"WHERE email_id = '{email_info['email_id']}'"
            execute(db,db.cursor(),query)


if __name__ == "__main__":
    main()