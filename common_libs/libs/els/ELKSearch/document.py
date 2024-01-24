from libs.els.ELKSearch.Utils.base import make_format
from libs.els.ELKSearch.Utils.document_utils import set_source


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
        self.body = dict()
        self.size = size
        self.page = size * from_

    def set_body(self,body: dict):
        self.body.update(body)

    def set_sort(self, sort_list: list):
        sort_option = {sort_item.field: sort_item.order for sort_item in sort_list}
        self.body["sort"] = sort_option

    def insert(self, doc_id: str):
        """
        document 데이터 추가
        """
        return self.connect.index(index=self.index, body=self.body, id=doc_id)

    def update(self, doc_id):
        """
        document update
        id 값을 이용해 document를 특정하고 body의 내용을 덮어쓰기 하는 기능
        :param doc_id: els에서 설정된 document id 값
        :return:
        """
        return self.connect.index(index=self.index, id=doc_id, body=self.body)

    def find(self, source: list = None) -> dict:
        """
        els 검색 기능
        특정 index에서 조건에 맞는 document를 출력
        :param source: 출력할 결과 컬럼명
        :return:
        """
        source = set_source(source)
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
        # pk_value가 1개 or 여러개
        del_query = make_format("query", "term", {pk_name: pk_value})
        # pk_value가 1개만
        # del_query = {"query": make_format("match", pk_name, pk_value)}
        self.connect.delete_by_query(index=self.index, body=del_query)

    def set_pagination(self, size: int = 0, from_: int = 0) -> None:
        """
        검색 결과를 어디서 부터 얼만큼 출력할지 설정하는 모듈
        find 모듈을 사용하기 전에 선행 되어야함
        """
        self.size = size
        self.page = size * from_

    def prefix(self, body: dict, source: list = None) -> dict:
        """
        :param body:
        :param source: 반환 받을 index의 필드 빈 list 값 이면 전체 출력
        :return:
        """
        source = set_source(source)
        prefix_query = make_format("query","prefix", body)
        return self.connect.search(
            index=self.index,
            body=prefix_query,
            size=self.size,
            _source=source
        )

    def count(self, body: dict) -> int:
        """
        :param body: elasticsearch에 전송할 query
        :return: query 결과로 나온 item 갯 수        """
        return self.connect.count(index=self.index, body=body)["count"]