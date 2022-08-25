from typing import Optional, Union, Dict, Any
from elasticsearch import Elasticsearch, helpers
from Utils.ESUtils import set_dict_list, make_query, set_find_option


class ESSearch:
    def __init__(
            self,
            host: str = "localhost",
            port: str = "9200",
            cur_from: int = 1,
            size: int = 10,
            index: str = "biz_meta"
    ):
        """
        set elasticsearch connect && DSL query setting function
        :param host: elasticsearch host ip addr, default = localhost
        :param port: elasticsearch ip port number, default = 9200
        :param index:
        :param cur_from: elasticsearch default value = 0
        :param size: elasticsearch default value = 10
        """
        self.host = host
        self.port = port
        self.size = size
        self.index = index
        self.cur_from = cur_from - 1
        self.conn = self.connect()
        self.body = self.set_body()

    def connect(self) -> object:
        es = Elasticsearch(f"http://{self.host}:{self.port}")
        return es

    def set_body(self) -> Dict[Any,Any]:
        self.body = {
            "from": 0,
            "size": 10,
            "sort": [],
            "query": {"bool": dict()}
        }
        return self.body

    def set_sort(self, sort: str) -> None:
        """
        :param sort:  type str, ex) "field_name:asc,field_name:desc"
        """
        self.body["sort"] = set_find_option(sort)

    def set_pagination(self) -> None:
        self.body["from"] = self.cur_from
        self.body["size"] = self.size

    def set_filter(self, filter_option: str) -> None:
        """
        :param filter_option:  type str, ex) "key1:val1,key2:val2"
        """
        filter_list = set_find_option(filter_option)
        if len(filter_list):
            self.body["query"]["bool"]["filter"] = set_dict_list(filter_list[0], "match")

    def set_match(self, keyword_dict: dict, operator: Optional[str] = None, field: str = "data_nm") -> None:
        """
        :param keyword_dict: type dict
        :param field: search field, type str
        :param operator: search operator, type str ex) (AND, OR)
        """
        if len(keyword_dict.values()):
            must_query_list = []
            option = "match"

            if len(keyword_dict[option]) and operator is None:
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

    def insert(self, body: dict, es_id: str) -> None:
        return self.conn.index(index=self.index, body=body, id=es_id)

    def insert_bulk(self, data: list):
        return helpers.bulk(self.conn, data, index=self.index)

    def update(self, body: dict, es_id: str):
        return self.conn.update(index=self.index, id=es_id, body=body)

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
