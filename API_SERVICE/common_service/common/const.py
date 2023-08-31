NOT_ALLOWED_TABLES = [""]
time_zone = "Asia/Seoul"


class EmailAuthTable:
    table_nm = ""
    key_column = ""

    @staticmethod
    def get_select_query(email: str) -> dict:
        return {
            "table_nm": EmailAuthTable.table_nm,
            "where_info": [
                {
                    "table_nm": EmailAuthTable.table_nm,
                    "key": EmailAuthTable.key_column,
                    "value": email,
                    "compare_op": "=",
                    "op": "",
                }
            ],
        }


# login_service/LoginTable과 같음
class UserInfoTable:
    table_nm = "tb_user_info"
    key_column = "user_id"

    @staticmethod
    def get_select_query(user_id: str) -> dict:
        return {
            "table_nm": UserInfoTable.table_nm,
            "where_info": [
                {
                    "table_nm": UserInfoTable.table_nm,
                    "key": UserInfoTable.key_column,
                    "value": user_id,
                    "compare_op": "=",
                    "op": "",
                }
            ],
        }

    @staticmethod
    def get_update_query(row: dict) -> dict:
        return {
            "method": "UPDATE",
            "table_nm": UserInfoTable.table_nm,
            "data": row,
            "key": [UserInfoTable.key_column]
        }