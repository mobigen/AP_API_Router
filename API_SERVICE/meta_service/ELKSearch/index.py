import os
import json
# ELKSearch 경로
ELSSearch_PATH = os.path.dirname(os.path.abspath(__file__))


class Index:
    def __init__(self, connect):
        self.connect = connect

    def all_index(self):
        return self.connect.cat.indices()

    def create(self, index: str, path: str = None) -> dict:
        if path is None:
            path = f"{ELSSearch_PATH}/mapping/{index}.json"

        with open(path, "r") as fp:
            mapping = json.load(fp)

        return self.connect.indices.create(index=index, body=mapping)

    def delete(self, index: str) -> dict:
        return self.connect.indices.delete(index=index, ignore=[400,404])
