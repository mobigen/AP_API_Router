from typing import List

from pydantic import BaseSettings


class SecretInfo(BaseSettings):
    secret_key: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    algorithm: str = "HS256"
    expire_min: int = 60
    cookie_name: str = "user-docean-access-token"
    token_data_column: List = [
        "user_id",
        "emp_id",
        "cmpno",
        "user_nm",
        "email",
        "dept_nm",
        "innt_aut_group_cd",
        "user_type",
        "tmp_aut_group_cd",
        "tmp_aut_alc_user",
        "tmp_aut_alc_date",
        "tmp_aut_exp_date",
        "innt_data_clas",
        "dept_cd",
    ]