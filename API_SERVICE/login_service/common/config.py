import json
import logging.config
import os
from functools import lru_cache
from typing import Union

from pydantic import BaseSettings, PostgresDsn, validator, SecretStr

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(f"project base_dir :: {base_dir}")


class DBInfo(BaseSettings):
    HOST: str = ""
    PORT: str = ""
    USER: str = ""
    PASS: SecretStr = ""
    BASE: str = ""

    def get_dsn(self):
        return ""


class PGInfo(DBInfo):
    type: str = "postgres"
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


class Settings(BaseSettings):
    BASE_DIR = base_dir
    DB_POOL_RECYCLE: int = 900
    DB_ECHO: bool = False
    RELOAD: bool = True
    TESTING: bool = True

    DB_INFO: DBInfo = DBInfo()
    DB_URL: Union[str, PostgresDsn] = None

    @validator("DB_URL", pre=True, always=True)
    def assemble_db_url(cls, v, values):
        if all(value is not None for value in values.values()):
            return values.get("DB_INFO").get_dsn()
        raise ValueError("Not all PostgreSQL database connection values were provided.")


class ProdSettings(Settings):
    RELOAD = False
    TESTING = False

    class Config:
        env_file = f"{base_dir}/.env"
        env_file_encoding = "utf-8"


class LocalSettings(Settings):
    TESTING: bool = False
    DB_POOL_RECYCLE: int = 900
    DB_ECHO: bool = True
    RELOAD: bool = False

    # DB_INFO = PGInfo(
    #     HOST="192.168.100.126", PORT="25432", USER="dpsi", PASS="hello.sitemng12#$", BASE="ktportal", SCHEMA="sitemng"
    # )

    DB_INFO: TiberoInfo = TiberoInfo(HOST="192.168.101.164", PORT="8629", USER="dhub", PASS="dhub1234", BASE="tibero")


class TestSettings(LocalSettings):
    ...


@lru_cache
def get_settings():
    env = os.getenv("APP_ENV", "prod")
    print(env)
    return {"local": LocalSettings(), "test": TestSettings(), "prod": ProdSettings()}[env]


settings = get_settings()
print(settings)

with open(os.path.join(base_dir, "logging.json")) as f:
    log_config = json.load(f)
    logging.config.dictConfig(log_config)
logger = logging.getLogger()
