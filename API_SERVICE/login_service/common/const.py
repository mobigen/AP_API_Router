from typing import Dict


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
EXPIRE_DELTA = 1


class LoginTable:
    table_nm = "usr_mgmt"

    def __init__(self, key_column: str = "id"):
        self.key_column = key_column

    def get_query_data(self, id_: str) -> Dict:
        return {
            "table_nm": self.table_nm,
            "where_info": [
                {
                    "table_nm": self.table_nm,
                    "key": self.key_column,
                    "value": id_,
                    "compare_op": "=",
                    "op": "",
                }
            ],
        }


class RegisterTable:
    table_nm = "usr_mgmt"

    @staticmethod
    def get_query_data(data: Dict) -> Dict:
        return {"method": "INSERT", "table_nm": RegisterTable.table_nm, "data": data}
