import os
import re
import ast
from pathlib import Path
from datetime import datetime
from collections import Counter
from ELKSearch.Utils.database_utils import (
    prepare_config,
    connect_db,
    select,
    config,
    execute,
)

root_path = str(Path(os.path.dirname(os.path.abspath(__file__))))


def main():
    """
    param:
    parameter는 els_update.py 에서 공통으로 사용
    - db_type: conf/config.ini or ELKSearch/conf/db_config.ini
    - check: type str, False or True, True=누적,False=갱신

    """
    prepare_config(root_path)
    db = connect_db()

    # 검색어 로그 불러오기
    search_file_name = (
        f"{root_path}/log/meta/{datetime.today().date().strftime('%Y%m%d')}_search.log"
    )
    with open(search_file_name, "r") as fp:
        search_log_file = fp.read().split("\n")[:-1]

    # 필터링할 단어 리스트 불러오기
    fword_file_name = f"{root_path}/ELKSearch/conf/bad_word.txt"
    with open(fword_file_name, "r") as fp:
        bad_word_list = fp.read().split("\n")

    # 자모만 들어가 있는 오타 제외
    today_search_word = []
    for words in search_log_file:
        result = [
            word
            for word in ast.literal_eval(words)
            if re.search("[ㄱ-ㅎㅏ-ㅣ]", word) is None
        ]
        today_search_word = today_search_word + result

    # 단어 필터링
    today_search_word = [
        word for word in today_search_word if word not in bad_word_list
    ]
    today_search_word = Counter(today_search_word)

    # check True : 누적 / False: 갱신
    if config.check == "True":
        query = "SELECT * FROM tb_recommend_keyword"
        recommend_word = select(db, query)[0]

        for word in recommend_word:
            key = word["keyword"]
            cnt = word["count"]
            if key in today_search_word.keys():
                today_search_word[key] = today_search_word[key] + cnt
            else:
                today_search_word[key] = cnt

    for word, cnt in today_search_word.most_common(10):
        query = (
            "INSERT INTO tb_recommend_keyword(keyword,count,use_yn)"
            f"VALUES ('{word}',{cnt}, 'N') ON CONFLICT (keyword) DO UPDATE "
            f"SET count = {cnt};"
        )
        execute(db, db.cursor(), query)


if __name__ == "__main__":
    main()
