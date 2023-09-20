import os
import logging
import pandas as pd

from pathlib import Path
from typing import Dict

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from libs.auth.keycloak import keycloak
from libs.disk.mydisk import mydisk
from mydisk_service.common.config import settings


logger = logging.getLogger()

class TreeParams(BaseModel):
    target_directory: str

    def get_path(self) -> Path:
        return Path(
            os.path.join(
                settings.MYDISK_ROOT_DIR,
                self.target_directory.lstrip("/") if self.target_directory.startswith("/") else self.target_directory,
            )
        )

class PreviewParam(BaseModel):
    target_file_directory: str
    rows: int

    def get_path(self) -> Path:
        return Path(
            os.path.join(
                settings.MYDISK_ROOT_DIR,
                self.target_file_directory.lstrip("/")
                if self.target_file_directory.startswith("/")
                else self.target_file_directory,
            )
        )


router = APIRouter()


@router.post("/v1/preview")
async def head(params: PreviewParam):
    try:
        path = params.get_path()
        lines = params.rows
        logger.info(path)
        df = pd.read_excel(path, header=None) if path.suffix in [".xls", ".xlsx"] else pd.read_csv(path, header=None)
        df = df.fillna("")
        result = {"result": 1, "errorMessage": "", "data": {"body": df[:lines].values.tolist()}}
    except Exception as e:
        result = {"result": 1, "errorMessage": str(e)}
    return result

@router.post("/v1/listdir")
async def walk(param: TreeParams) -> Dict:
    id = 0

    def nodes(p: Path):
        nonlocal id
        lst = []
        for i in p.iterdir():
            id += 1
            data = {"text": i.name, "id": id, "type": "file"}
            if i.is_dir():
                node = nodes(i)
                if node:
                    data["nodes"] = node
                data["type"] = "directory"

            lst.append(data)
        return lst

    try:
        result = {"result": 1, "errorMessage": "", "data": {"body": nodes(param.get_path())}}
    except FileNotFoundError as fe:
        result = {"result": 1, "errorMessage": str(fe), "data": []}
    except Exception as e:
        result = {"result": 0, "errorMessage": str(e), "data": []}
    return result

async def get_admin_token() -> None:
    res = await mydisk.generate_admin_token(
        username=settings.MYDISK_INFO.admin_username,
        password=settings.MYDISK_INFO.admin_password,
        scope=settings.MYDISK_INFO.scope,
        client_id=settings.MYDISK_INFO.client_id,
        client_secret=settings.MYDISK_INFO.client_secret,
    )
    logger.info(res)

    return res.get("data").get("access_token")