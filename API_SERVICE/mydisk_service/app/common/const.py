from typing import Dict


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
EXPIRE_DELTA = 1
COOKIE_NAME = "user-katech-access-token"

S3KEY = "WL5Z2I1BN0NBB60QAO1G"
S3SECRET = "Z7Gy5HhhdIRnsL4G2pDHzxV4Sb5fCsBBagkg9aWM"


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
