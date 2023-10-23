from typing import Union


class Base:
    table_nm: str
    key_column: Union[str, list]

    @classmethod
    def get_select_query(cls, key_value: str) -> dict:
        return {
            "table_nm": cls.table_nm,
            "where_info": [
                {
                    "table_nm": cls.table_nm,
                    "key": cls.key_column,
                    "value": key_value,
                    "compare_op": "=",
                    "op": "",
                }
            ],
        }

    @classmethod
    def get_execute_query(cls, method: str, row: dict) -> dict:
        query = {
            "method": method,
            "table_nm": cls.table_nm,
            "data": row,
            "key": cls.key_column if type(cls.key_column) is list else [cls.key_column],
        }
        if method.upper() == "INSERT":
            query.pop("key")
        return query
