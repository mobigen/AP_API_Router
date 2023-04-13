import os
from functools import lru_cache
from typing import Union

from pydantic import BaseSettings, PostgresDsn, validator

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(f"project base_dir :: {base_dir}")


class Settings(BaseSettings):
    BASE_DIR = base_dir
    DB_POOL_RECYCLE: int = 900
    DB_ECHO: bool = False
    RELOAD: bool = True
    TESTING: bool = True

    PG_HOST: str
    PG_PORT: int
    PG_USER: str
    PG_PASSWORD: str
    PG_DBNAME: str
    PG_SCHEMA: str

    DB_URL: Union[str, PostgresDsn] = None

    @validator("DB_URL", pre=True, always=True)
    def assemble_db_url(cls, v, values):
        print(f"v :: {v}")
        print(f"values :: {values}")
        if all(value is not None for value in values.values()):
            return str(
                PostgresDsn.build(
                    scheme="postgresql",
                    host=values.get("PG_HOST"),
                    port=str(values.get("PG_PORT")),
                    user=values.get("PG_USER"),
                    password=values.get("PG_PASSWORD"),
                    path=f"/{values.get('PG_DBNAME')}",
                )
            )
        raise ValueError("Not all PostgreSQL database connection values were provided.")


class ProdSettings(Settings):
    RELOAD = False
    TESTING = False

    class Config:
        env_file = f"{base_dir}/.env"
        env_file_encoding = "utf-8"


class LocalSettings(Settings):
    PG_HOST = "192.168.100.126"
    PG_PORT = 25432
    PG_USER = "dpmanager"
    PG_PASSWORD = "hello.dp12#$"
    PG_DBNAME = "ktportal"
    # PG_SCHEMA = "sitemng"
    PG_SCHEMA = "users,meta,sitemng,board,analysis,sysconfig"


class TestSettings(LocalSettings):
    ...


@lru_cache
def get_settings():
    env = os.getenv("APP_ENV", "prod")
    print(env)
    return {"local": LocalSettings(), "test": TestSettings(), "prod": ProdSettings()}[env]


settings = get_settings()
