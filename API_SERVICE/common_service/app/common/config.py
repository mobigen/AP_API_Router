import logging.config
import os
from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings, PostgresDsn

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(f"common base_dir :: {base_dir}")


class DBInfo(BaseSettings):
    DB_POOL_RECYCLE: int = 900
    DB_ECHO: bool = True
    DB_URL: str


class PGInfo(DBInfo):
    SCHEMA: str

    class Config:
        env_file = f"{base_dir}/.env"
        env_file_encoding = "utf-8"


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


class Settings(BaseSettings):
    BASE_DIR = base_dir
    RELOAD: bool
    TESTING: bool

    DB_INFO: DBInfo
    KEYCLOAK_INFO: KeycloakInfo


class ProdSettings(Settings):
    RELOAD = False
    TESTING = False

    DB_INFO = PGInfo()
    KEYCLOAK_INFO = KeycloakInfo()


class LocalSettings(Settings):
    TESTING: bool = False
    RELOAD: bool = False

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

    KEYCLOAK_INFO = KeycloakInfo(
        keycloak_url="https://auth.bigdata-car.kr",
        admin_username="admin",
        admin_password="2021@katech",
        realm="mobigen",
        client_id="katech",
        client_secret="ZWY7WDimS4rxzaXEfwEShYMMly00i8L0",
    )


class TestSettings(LocalSettings):
    TESTING = True
    RELOAD = True


@lru_cache
def get_settings() -> Settings:
    env = os.getenv("APP_ENV", "prod")
    print(f"env :: {env}")
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
        "filename": os.path.join(base_dir, "log", "common.log"),
        "mode": "a",
        "maxBytes": 20000000,
        "backupCount": 10,
        "level": "DEBUG",
        "formatter": "standard",
    }
    log_config["root"]["handlers"].append("file_handler")
logging.config.dictConfig(log_config)
