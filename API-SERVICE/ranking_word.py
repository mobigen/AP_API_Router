import os
import re
import ast
from pathlib import Path
from datetime import datetime
from collections import Counter
from ELKSearch.Utils.database_utils import prepare_config, connect_db, select, config, execute
root_path = str(Path(os.path.dirname(os.path.abspath(__file__))))


# todo: 이재중 책임님께 ranking용 db table 추가 명세 작성후 요청
def main():
    """
    param:
    parameter는 els_update.py 에서 공통으로 사용
    - db_type: conf/config.ini or ELKSearch/conf/db_config.ini
    - check: type str, False or True, True=누적,False=갱신

    """
    today = datetime.today().date().strftime('%Y%m%d')
    prepare_config(root_path)
    db = connect_db()

    # 검색어 로그 불러오기
    search_file_name = f"{root_path}/log/meta/{today}_search.log"
    with open(search_file_name,"r") as fp:
        search_log_file = fp.read().split("\n")[:-1]

    today_search_word = []
    for words in search_log_file:
        result = [word for word in ast.literal_eval(words)]
        today_search_word = today_search_word + result

    query = "INSERT INTO srhwd_find_tmscnt_sum VALUES "
    values = ""
    if len(today_search_word):
        for word, cnt in Counter(today_search_word).items():
            item = f"('{word}',{cnt},'{datetime.today().date()}'),"
            values = values + item
    query = query + values[:-1]
    execute(db,db.cursor(), query)


if __name__ == "__main__":
    main()