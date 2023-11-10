import re
import string
from elasticsearch import Elasticsearch


def set_els(host: str, port: int):
    return Elasticsearch(f"http://{host}:{port}")


def make_format(key, inner_key, value) -> dict:
    query = {key: {inner_key: value}}
    return query


def symbol_filter(keywords: str):
    words = " ".join(keywords).strip()
    words = re.sub(f"[{string.punctuation}]"," ",words)
    return words
