from typing import Dict


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
EXPIRE_DELTA = 1
COOKIE_NAME = "user-katech-access-token"


class LoginTable:
    table_nm = "tb_user_info"
    key_column = "user_id"

    @staticmethod
    def get_query_data(user_id: str) -> Dict:
        return {
            "table_nm": LoginTable.table_nm,
            "where_info": [
                {
                    "table_nm": LoginTable.table_nm,
                    "key": LoginTable.key_column,
                    "value": user_id,
                    "compare_op": "=",
                    "op": "",
                }
            ],
        }


class RegisterTable:
    table_nm = "tb_user_info"

    @staticmethod
    def get_query_data(data: Dict) -> Dict:
        return {"method": "INSERT", "table_nm": RegisterTable.table_nm, "data": data}

    @staticmethod
    def upsert_query_data(method: str, data: Dict) -> Dict:
        method = method.upper()
        queryDict = { "method": method, "table_nm": RegisterTable.table_nm, "data": data}
        if method == "UPDATE" :
            queryDict["key"] = ["user_id"]
        return queryDict


class IrisInfoTable:
    table_nm = "tb_iris_user_info"
    key_column = "user_id"

    def get_query_data(self, user_id: str) -> Dict:
        return {
            "table_nm": self.table_nm,
            "where_info": [
                {
                    "table_nm": self.table_nm,
                    "key": self.key_column,
                    "value": user_id,
                    "compare_op": "=",
                    "op": "",
                }
            ],
        }

    @staticmethod
    def upsert_query_data(method: str, data: Dict) -> Dict:
        method = method.upper()
        queryDict = { "method": method, "table_nm": IrisInfoTable.table_nm, "data": data}
        if method == "UPDATE":
            queryDict["key"] = ["user_id"]

        return queryDict

class EmailAuthTable:
    table_nm = "tb_email_athn_info"
    key_column = "email"

    @staticmethod
    def get_query_data(user_id: str) -> Dict:
        return {
            "table_nm": EmailAuthTable.table_nm,
            "where_info": [
                {
                    "table_nm": EmailAuthTable.table_nm,
                    "key": EmailAuthTable.key_column,
                    "value": user_id,
                    "compare_op": "=",
                    "op": "",
                }
            ],
        }

    @staticmethod
    def get_execute_query(data: Dict) -> Dict:
        queryDict = {
            "table_nm" :EmailAuthTable.table_nm,
            "key": [EmailAuthTable.key_column],
            "method": "UPDATE",
            "data": data,
        }

        return queryDict
