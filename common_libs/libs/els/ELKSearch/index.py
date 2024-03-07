import os
import json
# ELKSearch 경로
ELKSearch_PATH = os.path.dirname(os.path.abspath(__file__))


class Index:
    def __init__(self, connect):
        self.connect = connect

    def all_index(self) -> dict:
        """
        :return: key값이 index명, value는 alias 설정 값이다
        """
        return self.connect.indices.get_alias(index="*")

    def init_els_all_index(self, path: str):
        for index_file in os.listdir(path):
            if index_file[:-5] in self.all_index().keys():
                self.delete(index_file[:-5])
            self.create(index_file[:-5], path)

    def create(self, index: str, path: str = None) -> dict:
        """
        :param index: 생성할 index 이름
        :param path: 생성할 index의 mapping 파일 위치
        :return: els에 요청한 결과 성공/실패는 bool 타입으로 반환 된다
        """
        if path is None:
            path = f"{ELKSearch_PATH}/mapping/{index}.json"
        else:
            path = f"{path}/{index}.json"

        with open(path, "r") as fp:
            mapping = json.load(fp)

        return self.connect.indices.create(index=index, body=mapping)

    def delete(self, index: str) -> dict:
        """
        :param index: 삭제할 index의 이름
        :return: els에 요청한 결과 성공/실패는 bool 타입으로 반환 된다
        """
        return self.connect.indices.delete(index=index, ignore=[400,404])
