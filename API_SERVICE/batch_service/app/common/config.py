import logging.config
import os
from functools import lru_cache

from pydantic import BaseSettings, PostgresDsn, Field

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(f"batch base_dir :: {base_dir}")


class DBInfo(BaseSettings):
    DB_POOL_RECYCLE: int = Field(default=900)
    DB_ECHO: bool = Field(default=False)


class PGInfo(DBInfo):
    DB_URL: str
    SCHEMA: str

    class Config:  # TODO: Config 사용없이 개별로 env 읽어서 할당
        env_file = f"{base_dir}/.env"
        env_file_encoding = "utf-8"


class SeoulPGInfo(DBInfo):
    SEOUL_DB_URL: str = Field(..., alias="DB_URL")
    SEOUL_SCHEMA: str = Field(..., alias="SCHEMA")

    class Config:
        env_file = f"{base_dir}/.env"
        env_file_encoding = "utf-8"


class ELSInfo(BaseSettings):
    ELS_HOST: str = Field(..., alias="host")
    ELS_PORT: int = Field(..., alias="port")

    class Config:
        env_file = f"{base_dir}/.env"
        env_file_encoding = "utf-8"


class Settings(BaseSettings):
    BASE_DIR = base_dir
    RELOAD: bool
    TESTING: bool

    EMAIL_ADDR: str
    EMAIL_PASSWORD: str
    SMTP_SERVER: str
    SMTP_PORT: str

    DB_INFO: DBInfo
    SEOUL_DB_INFO: SeoulPGInfo
    ELS_INFO: ELSInfo


class ProdSettings(Settings):
    RELOAD = False
    TESTING = False

    DB_INFO = PGInfo()
    SEOUL_DB_INFO = SeoulPGInfo()
    ELS_INFO = ELSInfo()

    class Config:
        env_file = f"{base_dir}/.env"
        env_file_encoding = "utf-8"


class LocalSettings(Settings):
    TESTING: bool = False
    RELOAD: bool = False

    SMTP_SERVER = "smtp.office365.com"
    SMTP_PORT = "587"
    EMAIL_ADDR = "admin@bigdata-car.kr"
    EMAIL_PASSWORD = "Pas07054354@katech!"

    DB_INFO = PGInfo(
        DB_POOL_RECYCLE=900,
        DB_ECHO=False,
        SCHEMA="sitemng,users,meta,iag,ckan,board,analysis",
        DB_URL=str(
            PostgresDsn.build(
                scheme="postgresql",
                host="192.168.100.126",
                port="25432",
                user="dpmanager",
                password="hello.dp12#$",
                path="/dataportal",
            )
        ),
    )

    SEOUL_DB_INFO = SeoulPGInfo(
        DB_POOL_RECYCLE=900,
        DB_ECHO=False,
        SCHEMA="public",
        DB_URL=str(
            PostgresDsn.build(
                scheme="postgresql",
                host="147.47.200.145",
                port="34543",
                user="openplatform",
                password="openplatform",
                path="/katechdb",
            )
        ),
    )

    ELS_INFO = ELSInfo(host="192.168.101.44", port=39200)


class TestSettings(LocalSettings):
    TESTING = True
    RELOAD = True


@lru_cache
def get_settings() -> Settings:
    env = os.getenv("APP_ENV", "prod")
    print(env)
    return {"local": LocalSettings(), "test": TestSettings(), "prod": ProdSettings()}[env]


settings = get_settings()
print(settings)

log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] - %(message)s"},
    },
    "handlers": {
        "console_handler": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "standard",
        },
    },
    "root": {"level": "DEBUG", "handlers": ["console_handler"], "propagate": False},
}

if "prod" == os.getenv("APP_ENV", "prod"):
    log_config["handlers"]["file_handler"] = {
        "class": "logging.handlers.RotatingFileHandler",
        "filename": os.path.join(base_dir, "log", "batch.log"),
        "mode": "a",
        "maxBytes": 20000000,
        "backupCount": 10,
        "level": "INFO",
        "formatter": "standard",
    }
    log_config["root"]["handlers"].append("file_handler")
logging.config.dictConfig(log_config)
