import logging.config
import logging.config
import os
from functools import lru_cache

from pydantic import BaseSettings, PostgresDsn

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(f"router base_dir :: {base_dir}")


class DBInfo(BaseSettings):
    DB_POOL_RECYCLE: int = 900
    IS_ECHO: bool = True
    DB_URL: str


class PGInfo(DBInfo):
    SCHEMA: str

    class Config:
        env_file = f"{base_dir}/.env"
        env_file_encoding = "utf-8"


class Settings(BaseSettings):
    BASE_DIR = base_dir
    RELOAD: bool
    TESTING: bool

    DB_INFO: PGInfo


class ProdSettings(Settings):
    RELOAD = False
    TESTING = False

    DB_INFO: PGInfo = PGInfo()


class LocalSettings(Settings):
    TESTING: bool = False
    RELOAD: bool = False

    DB_INFO: PGInfo = PGInfo(
        DB_POOL_RECYCLE=900,
        IS_ECHO=True,
        DB_URL=str(
            PostgresDsn.build(
                scheme="postgresql",
                host="192.168.100.126",
                port="25432",
                user="dpmanager",
                password="hello.dp12#$",
                path=f"/dataportal",
            )
        ),
    )


class TestSettings(LocalSettings):
    TESTING = True
    RELOAD = True


@lru_cache
def get_settings():
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
        "file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "./log/router.log",
            "mode": "a",
            "maxBytes": 20000000,
            "backupCount": 10,
            "level": "DEBUG",
            "formatter": "standard",
        },
        "console_handler": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "standard",
        },
    },
    "root": {"level": "DEBUG", "handlers": ["file_handler", "console_handler"], "propagate": False},
}
logging.config.dictConfig(log_config)
