from typing import Optional, Union, Dict, Any
from elasticsearch import Elasticsearch, helpers
from Utils.ESUtils import set_dict_list, make_query


class ESSearch:
    def __init__(
            self,
            host: str = "192.168.101.44",
            port: str = "39200",
            cur_from: int = 1,
            size: int = 10,
            index: str = "biz_meta"
    ):
        """
        set elasticsearch connect && DSL query setting function
        :param host: elasticsearch host ip addr, default = localhost
        :param port: elasticsearch ip port number, default = 9200
        :param index:
        :param cur_from: curPage, elasticsearch default value = 0
        :param size: perPage, elasticsearch default value = 10
        """
        self.host = host
        self.port = port
        self.size = size
        self.index = index
        self.cur_from = cur_from
        self.conn = self.connect()
        self.body = self.set_body()

    def connect(self) -> object:
        es = Elasticsearch(f"http://{self.host}:{self.port}")
        return es

    def set_body(self) -> Dict[Any,Any]:
        self.body = {
            "from": self.cur_from,
            "size": self.size,
            "sort": [],
            "query": {"bool": dict()}
        }
        return self.body

    def set_sort(self, sort: list) -> None:
        self.body["sort"] = sort

    def set_pagination(self) -> None:
        self.body["from"] = self.cur_from
        self.body["size"] = self.size

    def set_filter(self, filter_option: dict, filter_oper: str = "OR") -> None:
        filter_list = []
        if filter_oper == "OR":
            query = " ".join([" ".join(values) for values in filter_option.values()])
            fields = list(filter_option.keys())
            self.body["query"]["bool"]["filter"] = [{"multi_match":{"query":query,"fields":fields}}]
        else:
            for option, items in filter_option.items():
                filter_list.extend([make_query("match",option,item) for item in items])
            self.body["query"]["bool"]["filter"] = filter_list

    def set_match(self, keyword_dict: dict, operator: Optional[str] = "AND", field: str = "data_nm.korean_analyzer") -> None:
        """
        :param keyword_dict: type dict
        :param field: search field, type str
        :param operator: search operator, type str ex) (AND, OR)
        """
        if len(keyword_dict.values()):
            must_query_list = []
            option = "match"

            if len(keyword_dict[option]) and operator.upper() == "AND":
                must_query_list = set_dict_list(keyword_dict[option], option, field)

            if len(keyword_dict["match_phrase"]):
                option = "match_phrase"
                must_query_list = set_dict_list(keyword_dict[option],option,field)

            if len(keyword_dict[option]) and operator.upper() == "OR":
                keyword = " ".join(keyword_dict[option])
                op_query_dict = make_query(field, "query", keyword)
                op_query_dict[field]["operator"] = operator
                term = make_query(option, field, op_query_dict[field])
                must_query_list.append(term)
            self.body["query"]["bool"]["must"] = must_query_list
        else:
            self.body["query"]["bool"]["must"] = {"match_all": {}}

    def insert(self, body: dict, doc_id: str) -> None:
        return self.conn.index(index=self.index, body=body, id=doc_id)

    def insert_bulk(self, data: list):
        return helpers.bulk(self.conn, data, index=self.index)

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

    def search(self) -> Dict[Any, Any]:
        return self.conn.search(index=self.index, body=self.body)
