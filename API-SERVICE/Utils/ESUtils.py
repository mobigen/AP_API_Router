from elasticsearch import Elasticsearch
from pydantic import BaseModel


def is_space(text:str) -> int:
    if " " in text:
        return 1
    else:
        return 0


def connect_es(host: str = "localhost",port: str = "9200"):
    es = Elasticsearch(f"http://{host}:{port}")
    return es


def make_query(op,field,value):
    query = {op: {field: value}}
    return query


class ESSearch:
    def __init__(self,host: str = "localhost",
                 port: str = "9200",
                 cur_from: int = 0,
                 size: int = 10,
                 index: str = "biz_meta",
                 sort_list: list = []):
        """

        :param cur_from: elasticsearch default value = 0
        :param size: elasticsearch default value = 10
        """
        self.host = host
        self.port = port
        self.size = size
        self.index = index
        self.cur_from = cur_from
        self.sort_list = sort_list
        self.keyword_dict = dict()
        self.es = self.connect()
        self.base_query = self.set_base_query()

    def connect(self) -> object:
        es = Elasticsearch(f"http://{self.host}:{self.port}")
        return es

    def set_base_query(self) -> dict:
        base_query = {
            "from": self.cur_from,
            "size": self.size,
            "sort": self.sort_list,
            "query": {"bool": dict()}
        }
        return base_query

    def div_keyword(self,keyword_list: list):
        self.keyword_dict = {
            "match_phrase": [],
            "match": []
        }
        for keyword in keyword_list:
            k = keyword.replace(" ","")
            if len(k) < 1:
                continue
            if is_space(keyword):
                self.keyword_dict["match_phrase"].append(keyword)
            else:
                self.keyword_dict["match"].append(keyword)

    def set_filter(self,filter_dict:dict):
        filter_query = []
        if len(filter_dict.values()):
            for field,value in filter_dict.items():
                filter_condition = make_query("match",field,value)
                filter_query.append(filter_condition)
            self.base_query["query"]["bool"]["filter"] = filter_query

    def set_match(self, operator: str = None):
        must_query_list = []
        if len(self.keyword_dict.values()):
            if len(self.keyword_dict["match"]) and operator in ["or","OR"]:
                op_query_dict = make_query("data_nm", "query", ' '.join(self.keyword_dict["match"]))
                op_query_dict["data_nm"]["operator"] = operator
                term = make_query("match", "data_nm", op_query_dict["data_nm"])
                must_query_list.append(term)
            if len(self.keyword_dict["match"]) and operator is None:
                for keyword in self.keyword_dict["keywords"]:
                    term = make_query("match","data_nm",keyword)
                    must_query_list.append(term)
            if len(self.keyword_dict["match_phrase"]):
                for phrase_key in self.keyword_dict["phrase"]:
                    phrase = make_query("match_phrase","data_nm",phrase_key)
                    must_query_list.append(phrase)
        else:
            query = {"match_all": {}}
            must_query_list.append(query)

        self.base_query["query"]["bool"]["must"] = must_query_list
