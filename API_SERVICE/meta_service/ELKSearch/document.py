from meta_service.ELKSearch.Utils.base import set_body


class DocumentManager:
    def __init__(self, connect, index: str, size: int = 0, from_:int = 0):
        """
        :param connect: Elasticsearch instance
        :param index: document를 사용할 index명 (DB의 table명과 유사)
        :param size: 검색 결과 얼만큼 출력해 줄지 결정할 사이즈
        :param from_: 검색 결과를 어디서 부터 출력해 줄지 결정할 사이즈
        """
        self.connect = connect
        self.index = index
        self.body = set_body()
        self.size = size
        self.page = size * from_

    def create(self):
        pass

    def update(self):
        pass

    def find(self, source: list = ...) -> dict:
        """
        els 검색 기능
        특정 index에서 조건에 맞는 document를 출력
        """
        return self.connect.search(
            index=self.index,
            body=self.body,
            from_=self.page,
            size=self.size,
            _source=source
        )

    def delete(self):
        pass

    def set_pagination(self, size: int, from_: int) -> None:
        """
        검색 결과를 어디서 부터 얼만큼 출력할지 설정하는 모듈
        find 모듈을 사용하기 전에 선행 되어야함
        """
        self.size = size
        self.page = size * from_
