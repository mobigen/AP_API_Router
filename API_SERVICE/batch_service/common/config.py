import json
import logging.config
import os
from functools import lru_cache
from typing import Union

from pydantic import BaseSettings, PostgresDsn, validator, SecretStr

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(f"batch base_dir :: {base_dir}")


class DBInfo(BaseSettings):
    HOST: str = ""
    PORT: str = ""
    USER: str = ""
    PASS: SecretStr = ""
    BASE: str = ""
    SCHEMA: str = ""

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


class SeoulPGInfo(DBInfo):
    type: str = "orm"
    SEOUL_HOST: str = ""
    SEOUL_PORT: str = ""
    SEOUL_BASE: str = ""
    SEOUL_USER: str = ""
    SEOUL_PASS: SecretStr = ""
    SEOUL_SCHEMA: str = ""

    def settings(self):
        self.HOST = self.SEOUL_HOST
        self.PORT = self.SEOUL_PORT
        self.BASE = self.SEOUL_BASE
        self.USER = self.SEOUL_USER
        self.PASS = self.SEOUL_PASS
        self.SCHEMA = self.SEOUL_SCHEMA
        return self

    def get_dsn(self):
        return str(
            PostgresDsn.build(
                scheme="postgresql",
                host=self.SEOUL_HOST,
                port=self.SEOUL_PORT,
                user=self.SEOUL_USER,
                password=self.SEOUL_PASS.get_secret_value(),
                path=f"/{self.SEOUL_BASE}",
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
    SEOUL_DB_INFO: SeoulPGInfo = SeoulPGInfo()
    DB_URL: Union[str, PostgresDsn] = None
    SEOUL_DB_URL: Union[str, PostgresDsn] = None

    @validator("DB_URL", pre=True, always=True)
    def assemble_db_url(cls, v, values):
        if all(value is not None for value in values.values()):
            return values.get("DB_INFO").get_dsn()
        raise ValueError("Not all PostgreSQL database connection values were provided.")

    @validator("SEOUL_DB_URL", pre=True, always=True)
    def assemble_seoul_db_url(cls, v, values):
        if all(value is not None for value in values.values()):
            return values.get("SEOUL_DB_INFO").get_dsn()
        raise ValueError("Not all PostgreSQL database connection values were provided.")


class ProdSettings(Settings):
    TESTING: bool = False
    DB_POOL_RECYCLE: int = 900
    DB_ECHO: bool = True
    RELOAD: bool = False

    DB_INFO: PGInfo = PGInfo()
    SEOUL_DB_INFO: SeoulPGInfo = SeoulPGInfo()


class LocalSettings(Settings):
    TESTING: bool = False
    DB_POOL_RECYCLE: int = 900
    DB_ECHO: bool = True
    RELOAD: bool = False

    DB_INFO = PGInfo(
        HOST="192.168.100.126",
        PORT="25432",
        USER="dpmanager",
        PASS="hello.dp12#$",
        BASE="dataportal",
        SCHEMA="sitemng,users,meta,ckan",
    )

    SEOUL_DB_INFO = SeoulPGInfo(
        SEOUL_HOST="147.47.200.145",
        SEOUL_PORT="34543",
        SEOUL_USER="openplatform",
        SEOUL_PASS="openplatform",
        SEOUL_BASE="katechdb",
        SEOUL_SCHEMA="public",
    )


class TestSettings(LocalSettings):
    ...


@lru_cache
def get_settings() -> Settings:
    env = os.getenv("APP_ENV", "prod")
    print(env)
    return {"local": LocalSettings(), "test": TestSettings(), "prod": ProdSettings()}[env]


settings = get_settings()
settings.SEOUL_DB_INFO = settings.SEOUL_DB_INFO.settings()
print(settings)

with open(os.path.join(base_dir, "logging.json")) as f:
    log_config = json.load(f)
    logging.config.dictConfig(log_config)
