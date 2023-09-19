import json
import logging.config
import os
from functools import lru_cache
from typing import Optional, Union

from pydantic import BaseSettings, PostgresDsn, validator, SecretStr, AnyUrl

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(f"login base_dir :: {base_dir}")

class DBInfo(BaseSettings):
    HOST: str = ""
    PORT: str = ""
    USER: str = ""
    PASS: SecretStr = ""
    BASE: str = ""

    class Config:
        env_file = f"{base_dir}/.env"
        env_file_encoding = "utf-8"

    def get_dsn(self):
        return ""


class PGInfo(DBInfo):
    type: str = "orm"
    SCHEMA: str = ""

    def get_dsn(self):
        return str(
            PostgresDsn.build(
                scheme="postgresql",
                host=self.HOST,
                port=self.PORT,
                user=self.USER,
                password=self.PASS.get_secret_value(),
                path=f"/{self.BASE}",
            )
        )


class TiberoInfo(DBInfo):
    type: str = "tibero"

    def get_dsn(self):
        return f"DSN={self.BASE};UID={self.USER};PWD={self.PASS.get_secret_value()}"

class KeycloakInfo(BaseSettings):
    keycloak_url: Optional[str]
    admin_username: Optional[str]
    admin_password: Optional[str]
    realm: Optional[str]
    client_id: Optional[str]
    client_secret: Optional[str]

    class Config:
        env_file = f"{base_dir}/.env"
        env_file_encoding = "utf-8"

class MydiskInfo(BaseSettings):
    mydisk_url: Optional[str]
    admin_username: Optional[str]
    admin_password: Optional[str]
    scope: Optional[str]
    client_id: Optional[str]
    client_secret: Optional[str]

    class Config:
        env_file = f"{base_dir}/.env"
        env_file_encoding = "utf-8"

class Settings(BaseSettings):
    BASE_DIR = base_dir
    DB_POOL_RECYCLE: int = 900
    DB_ECHO: bool = False
    RELOAD: bool = True
    TESTING: bool = True

    MYDISK_ROOT_DIR: str
    MYDISK_CONN_URL: AnyUrl

    DB_INFO: DBInfo = DBInfo()
    DB_URL: Union[str, PostgresDsn] = None

    KEYCLOAK_INFO: KeycloakInfo = KeycloakInfo()

    @validator("DB_URL", pre=True, always=True)
    def assemble_db_url(cls, v, values):
        if all(value is not None for value in values.values()):
            return values.get("DB_INFO").get_dsn()
        raise ValueError("Not all PostgreSQL database connection values were provided.")


class ProdSettings(Settings):
    TESTING: bool = False
    DB_POOL_RECYCLE: int = 900
    DB_ECHO: bool = True
    RELOAD: bool = False

    MYDISK_ROOT_DIR = "./"
    MYDISK_CONN_URL: AnyUrl = "https://mydisk.bigdata-car.kr"

    DB_INFO: PGInfo = PGInfo()

    KEYCLOAK_INFO = KeycloakInfo(
        keycloak_url="https://auth.bigdata-car.kr",
        admin_username="admin",
        admin_password="2021@katech",
        realm="kadap",
        client_id="katech",
        client_secret="pwLZG5EaWph1nJAOjwYJ32YGtXdAj5SL",
    )

    MYDISK_INFO = MydiskInfo(
        mydisk_url="https://mydisk.bigdata-car.kr",
        admin_username="superuser",
        admin_password="35ldxxhbd1",
        scope="upload profile admin list",
        client_id="86e9aaff5afc7d7828035500e11cb48c",
        client_secret="lfb5RQK9SH3GcRqGgq0QcLlW5mJf0JDBNkrn1729"
    )

class LocalSettings(Settings):
    TESTING: bool = False
    DB_POOL_RECYCLE: int = 900
    DB_ECHO: bool = True
    RELOAD: bool = False

    MYDISK_ROOT_DIR = "./"
    MYDISK_CONN_URL: AnyUrl = "https://mydisk.bigdata-car.kr"

    DB_INFO = PGInfo(
        HOST="192.168.100.126",
        PORT="25432",
        USER="dpmanager",
        PASS="hello.dp12#$",
        BASE="dataportal",
        SCHEMA="sitemng,users,meta,iag,ckan,board,analysis",
    )

    #KEYCLOAK_INFO = KeycloakInfo(
    #    keycloak_url="http://192.168.101.44:8080",
    #    admin_username="admin",
    #    admin_password="zxcv1234!",
    #    realm="kadap",
    #    client_id="uyuni",
    #    client_secret="8UDolCR5j1vHt4rsyHnwTDlYkuRmOUp8",
    #)

    KEYCLOAK_INFO = KeycloakInfo(
        keycloak_url="https://auth.bigdata-car.kr",
        admin_username="admin",
        admin_password="2021@katech",
        realm="mobigen",
        client_id="katech",
        client_secret="pwLZG5EaWph1nJAOjwYJ32YGtXdAj5SL",
    )

    MYDISK_INFO = MydiskInfo(
        mydisk_url="https://mydisk.bigdata-car.kr",
        admin_username="superuser",
        admin_password="35ldxxhbd1",
        scope="upload profile admin list",
        client_id="86e9aaff5afc7d7828035500e11cb48c",
        client_secret="lfb5RQK9SH3GcRqGgq0QcLlW5mJf0JDBNkrn1729"
    )

@lru_cache
def get_settings() -> Settings:
    env = os.getenv("APP_ENV", "prod")
    print(env)
    return {"local": LocalSettings(), "prod": ProdSettings()}[env]


settings = get_settings()
print(settings)

with open(os.path.join(base_dir, "logging.json")) as f:
    log_config = json.load(f)
    logging.config.dictConfig(log_config)
