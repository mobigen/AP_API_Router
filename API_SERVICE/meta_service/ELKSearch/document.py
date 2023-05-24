from meta_service.ELKSearch.Utils.base import set_body, make_format


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

    def insert(self):
        """
        document 데이터 추가
        """
        return self.connect.index(index=self.index, body=self.body)

    def update(self, doc_id):
        """
        document update
        id 값을 이용해 document를 특정하고 body의 내용을 덮어쓰기 하는 기능
        :param doc_id: els에서 설정된 document id 값
        :return:
        """
        return self.connect.update(index=self.index, id=doc_id, body=self.body)

    def find(self, source: list = ...) -> dict:
        """
        els 검색 기능
        특정 index에서 조건에 맞는 document를 출력
        :param source: 출력할 결과 컬럼명
        :return:
        """
        return self.connect.search(
            index=self.index,
            body=self.body,
            from_=self.page,
            size=self.size,
            _source=source
        )

    def delete(self, pk_name: str, pk_value):
        """
        els document 삭제 기능
        특정 document를 검색해서 검색 결과에 해당하는 항목을 삭제함
        pk_name,pk_value가 유니크한 값이 아니면 여러개의 항목이 삭제될 수 있음
        :param pk_name: 삭제할 데이터를 특정하기 위한 컬럼명
        :param pk_value: 삭제할 데이터를 특정하기 위한 변수
        :return:
        """
        del_query = {"query": make_format("match", pk_name, pk_value)}
        self.connect.delete_by_query(index=self.index, body=del_query)

    def set_pagination(self, size: int = 0, from_: int = 0) -> None:
        """
        검색 결과를 어디서 부터 얼만큼 출력할지 설정하는 모듈
        find 모듈을 사용하기 전에 선행 되어야함
        """
        self.size = size
        self.page = size * from_

    def prefix(self, body: dict, source: list = ...) -> dict:
        """
        :param body:
        :param source:
        :return:
        """
        prefix_query = make_format("query","prefix", body)
        return self.connect.search(
            index=self.index,
            body=prefix_query,
            size=self.size,
            _source=source
        )
