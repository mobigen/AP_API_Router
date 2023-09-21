import re
import ast
import logging
from datetime import datetime
from collections import Counter

from batch_service.database.conn import db
from batch_service.common.const import log_dir, RecommendKeyTable


logger = logging.getLogger()


def main():
    """
    """
    with db.get_db_manager() as session:
        # 검색어 로그 불러오기
        search_file_name = (
            f"{log_dir}/{datetime.today().date().strftime('%Y%m%d')}_search.log"
        )
        with open(search_file_name, "r") as fp:
            search_log_file = fp.read().split("\n")[:-1]

        # 필터링할 단어 리스트 불러오기
        fword_file_name = f"{service_dir}/batch_service/common/bad_word.txt"
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

        for word, cnt in today_search_word.most_common(10):
            data = {
                "word": word,
                "cnt": cnt,
                "use_yn": "N"
            }
            if session.query(**RecommendKeyTable.get_select_query(word)).first():
                session.execute(**RecommendKeyTable.get_execute_query("update",data))
            else:
                session.execute(**RecommendKeyTable.get_execute_query("insert",data))

            # session.execute(**RecommendKeyTable.get_execute_query("upsert", update_data))
