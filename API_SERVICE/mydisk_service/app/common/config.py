import logging.config
import os
from functools import lru_cache
from typing import Optional
from urllib.parse import quote

from pydantic import BaseSettings, Field, PostgresDsn

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(f"mydisk base_dir :: {base_dir}")


class DBInfo(BaseSettings):
    DB_POOL_RECYCLE: int = 900
    DB_ECHO: bool = True
    DB_URL: str


class PGInfo(DBInfo):
    SCHEMA: str


class KeycloakInfo(BaseSettings):
    KEYCLOAK_URL: Optional[str]
    ADMIN_USERNAME: Optional[str]
    ADMIN_PASSWORD: Optional[str]
    REALM: Optional[str]
    CLIENT_ID: Optional[str]
    CLIENT_SECRET: Optional[str]


class MydiskInfo(BaseSettings):
    ROOT_DIR: str

    MYDISK_URL: Optional[str]
    ADMIN_USERNAME: Optional[str]
    ADMIN_PASSWORD: Optional[str]
    SCOPE: Optional[str]
    CLIENT_ID: Optional[str]
    CLIENT_SECRET: Optional[str]


class S3Info(BaseSettings):
    S3_URL: str = Field(..., env="S3_URL")
    S3_KEY: str = Field(..., env="S3_KEY")
    S3_SECRET: str = Field(..., env="S3_SECRET")


class Settings(BaseSettings):
    BASE_DIR = base_dir
    RELOAD: bool
    TESTING: bool

    DB_INFO: DBInfo
    KEYCLOAK_INFO: KeycloakInfo
    MYDISK_INFO: MydiskInfo
    S3_INFO: S3Info


class ProdSettings(Settings):
    TESTING: bool = False
    RELOAD: bool = False

    LABEL_FILE_BASE: Optional[str] = None

    DB_INFO: PGInfo = PGInfo()
    KEYCLOAK_INFO: KeycloakInfo = KeycloakInfo()
    MYDISK_INFO: MydiskInfo = MydiskInfo()
    S3_INFO: S3Info = S3Info()



class LocalSettings(Settings):
    TESTING: bool = False
    RELOAD: bool = False

    LABEL_FILE_BASE: Optional[str] = "/home/deep/workspace/ysw/katech/filebrowser_datas/file_data/ADMIN/"

    DB_INFO = PGInfo(
        DB_POOL_RECYCLE=900,
        DB_ECHO=False,
        SCHEMA="sitemng,users,meta,iag,ckan,board,analysis",
        DB_URL=str(
            PostgresDsn.build(
                scheme="postgresql",
                host="localhost",
                port="5432",
                user="dpmanager",
                password=quote("hello.dp12#$", safe=""),
                path="/dataportal",
            )
        ),
    )

    KEYCLOAK_INFO = KeycloakInfo(
        KEYCLOAK_URL="https://auth.bigdata-car.kr",
        ADMIN_USERNAME="admin",
        ADMIN_PASSWORD="2021@katech",
        REALM="mobigen",
        CLIENT_ID="katech",
        CLIENT_SECRET="ZWY7WDimS4rxzaXEfwEShYMMly00i8L0",
    )

    MYDISK_INFO = MydiskInfo(
        ROOT_DIR="./",
        MYDISK_URL="https://mydisk.bigdata-car.kr",
        ADMIN_USERNAME="superuser",
        ADMIN_PASSWORD="35ldxxhbd1",
        SCOPE="download",
        CLIENT_ID="86e9aaff5afc7d7828035500e11cb48c",
        CLIENT_SECRET="lfb5RQK9SH3GcRqGgq0QcLlW5mJf0JDBNkrn1729",
    )

    S3_INFO = S3Info(
        S3_URL="http://10.10.30.51:8085",
        S3_KEY="",
        S3_SECRET=""
    )


@lru_cache
def get_settings() -> Settings:
    env = os.getenv("APP_ENV", "prod")
    print(env)
    return {"local": LocalSettings(), "prod": ProdSettings()}[env]


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
        "filename": os.path.join(base_dir, "log", "mydisk.log"),
        "mode": "a",
        "maxBytes": 20000000,
        "backupCount": 10,
        "level": "INFO",
        "formatter": "standard",
    }
    log_config["root"]["handlers"].append("file_handler")
logging.config.dictConfig(log_config)
