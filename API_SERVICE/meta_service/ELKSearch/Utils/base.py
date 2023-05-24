import re
import string
from elasticsearch import Elasticsearch


def set_els(server_info):
    return Elasticsearch(f"http://{server_info.host}:{server_info.port}")


def make_format(key, inner_key, value) -> dict:
    query = {key: {inner_key: value}}
    return query


def symbol_filter(keywords: str):
    words = " ".join(keywords).strip()
    words = re.sub(f"[{string.punctuation}]"," ",words)
    return words


def set_body():
    return {"sort": []}
