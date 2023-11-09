import abc
from typing import TypeVar, Tuple, List, Dict

from fastapi import FastAPI

T = TypeVar("T", bound="Executor")


class Connector(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def init_app(self, app: FastAPI, **kwargs):
        ...

    @abc.abstractmethod
    def get_db(self) -> T:
        ...


class Executor(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def query(self, **kwargs) -> T:
        ...

    @abc.abstractmethod
    def all(self) -> Tuple[List[dict], int]:
        ...

    @abc.abstractmethod
    def first(self) -> dict:
        ...

    @abc.abstractmethod
    def execute(self, **kwargs):
        ...

    @abc.abstractmethod
    def get_column_info(self, table_nm, schema=None) -> List[Dict[str, str]]:
        ...

    @abc.abstractmethod
    def close(self):
        ...

    @abc.abstractmethod
    def commit(self):
        ...

    @abc.abstractmethod
    def rollback(self):
        ...
