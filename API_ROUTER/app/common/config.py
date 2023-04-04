import logging.config
import os
from functools import lru_cache

from pydantic import BaseSettings, SecretStr

from .logging import log_config

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Settings(BaseSettings):
    BASE_DIR = base_dir
    DB_POOL_RECYCLE: int
    DB_ECHO: bool
    RELOAD: bool
    TESTING: bool

    PG_HOST: str
    PG_PORT: int
    PG_USER: str
    PG_PASS: SecretStr
    PG_BASE: str
    PG_SCHEMA: str


class ProdSettings(Settings):
    DB_POOL_RECYCLE: int = 900
    DB_ECHO: bool = True
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

    PG_HOST: str = "192.168.100.126"
    PG_PORT: int = 25432
    PG_USER: str = "dpsi"
    PG_PASS: SecretStr = "hello.sitemng12#$"
    PG_BASE: str = "ktportal"
    PG_SCHEMA: str = "sitemng"


class TestSettings(LocalSettings):
    TESTING = True
    RELOAD = True


@lru_cache
def get_settings():
    env = os.getenv("APP_ENV", "prod")
    return {"local": LocalSettings(), "test": TestSettings(), "prod": ProdSettings()}[env]


settings = get_settings()

logging.config.dictConfig(log_config)
logger = logging.getLogger(os.getenv("APP_ENV", "prod"))
