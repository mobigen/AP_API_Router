from typing import Dict, Any, Union
from elasticsearch import Elasticsearch
from ELKSearch.Utils.elasticsearch_utils import make_query


class ElasticSearchManager:
    def __init__(
            self,
            host: str = "10.217.59.133",
            port: str = "9200",
            page: int = 1,
            size: int = 10,
            index: str = "biz_meta",
    ):
        """
        set elasticsearch connect && DSL query setting function
        :param host: elasticsearch host ip addr, default = localhost
        :param port: elasticsearch ip port number, default = 9200
        :param index:
        :param page: page, size * page , elasticsearch default value = 0
        :param size: 아이템 개수 , elasticsearch default value = 10
        """
        self.host = host
        self.port = port
        self.size = size
        self.index = index
        self.cur_from = size * page
        self.conn = self.connect()
        self.body = self.set_default_option()

    def connect(self) -> Elasticsearch:
        es = Elasticsearch(f"http://{self.host}:{self.port}")
        return es

    def set_default_option(self) -> Dict[Any, Any]:
        # 유지 보수를 위해 model 적용 안 함
        self.body = {
            "sort": [],
        }
        return self.body

    def set_sort(self, sort: list) -> None:
        self.body["sort"] = sort

    def set_pagination(self,size: int, from_: int) -> None:
        self.size = size
        self.cur_from = size * from_

    def search(self, source=...):
        return self.conn.search(index=self.index, body=self.body, from_=self.cur_from,
                                size=self.size,_source=source)

    def insert(self, body: dict, doc_id: str) -> None:
        return self.conn.index(index=self.index, body=body, id=doc_id)

    def update(self, body: dict, doc_id: str):
        return self.conn.update(index=self.index, id=doc_id, body=body)

    def delete(self, field: str, data: Union[str, list]):
        """
        단수 : { query: { term: _id}}
        복수 : { query : { term : []}}
        :param field: data type str, elasticsearch index _source name
        :param data: data type str or list
        """
        delete_data = {field: data}
        delete_command = make_query("query", "term", delete_data)
        return self.conn.delete_by_query(index=self.index,body=delete_command)

    def prefix(self, keyword: dict, source=...):
        prefix_query = make_query("query","prefix", keyword)
        return self.conn.search(index=self.index, body=prefix_query, size=self.size, _source=source)
