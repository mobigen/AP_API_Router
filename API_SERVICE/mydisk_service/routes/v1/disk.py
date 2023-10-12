import os
import zipfile
import logging
import shutil
import base64
import pandas as pd

from PIL import Image
from io import BytesIO
from pathlib import Path
from typing import Optional, Union, Dict

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from libs.disk.mydisk import mydisk
from mydisk_service.common.config import settings

logger = logging.getLogger()


class UserParams(BaseModel):
    uuid: str

    def get_path(self) -> Path:
        return Path(
            os.path.join(
                settings.MYDISK_ROOT_DIR,
                "USER",
                self.uuid,
            )
        )


class DownloadParams(BaseModel):
    src_target_path: str

    def get_path(self) -> Path:
        return Path(
            os.path.join(
                settings.MYDISK_ROOT_DIR,
                self.src_target_path.lstrip("/") if self.src_target_path.startswith("/") else self.src_target_path,
            )
        )


class CopyParams(BaseModel):
    src_path: str
    force: Union[bool, str]
    dst_path: str

    def is_force(self):
        if isinstance(self.force, bool):
            return self.force
        elif self.force in ("yes", "true", "t", "y", "1"):
            return True
        return False

    def get_src(self):
        return os.path.join(
            settings.MYDISK_ROOT_DIR, self.src_path.lstrip("/") if self.src_path.startswith("/") else self.src_path
        )

    def get_dst(self):
        return os.path.join(
            settings.MYDISK_ROOT_DIR, self.dst_path.lstrip("/") if self.dst_path.startswith("/") else self.dst_path
        )


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
    width: Optional[int] = 90
    height: Optional[int] = 90
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
        width = params.width
        height = params.height
        suffix = path.suffix[1:].lower()
        lines = params.rows
        logger.info(f"path :: {path}")
        file_type = "txt"

        if suffix in ["jpg", "jpeg", "png", "gif", "tiff"]:
            file_type = "image"
            byte_str = BytesIO()
            thumb_image = Image.open(path)
            thumb_image.thumbnail((width, height))
            thumb_image.save(byte_str, format="png")
            image_base64str = base64.b64encode(byte_str.getvalue())
            logger.info(f"image str :: {image_base64str[:30]}...")
            contents = image_base64str
        else:  # txt, csv
            df = pd.read_excel(path, header=None) if path.suffix in ["xls", "xlsx"] else pd.read_csv(path, header=None)
            df = df.fillna("")
            contents = df[:lines].values.tolist()

        result = {"result": 1, "errorMessage": "", "data": {"body": contents}, "type": file_type}
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
        result = {"result": 0, "errorMessage": str(fe), "data": []}
    except Exception as e:
        result = {"result": 0, "errorMessage": str(e), "data": []}
    return result


@router.post("/v1/link")
async def hardlink(params: CopyParams):
    try:
        run(params.get_src(), params.get_dst(), params.is_force(), False)
        result = {"result": 1, "errorMessage": "", "data": {"body": 200}}
    except Exception as e:
        result = {"result": 0, "errorMessage": str(e)}
    return result


@router.post("/v1/copy")
async def copy(params: CopyParams):
    try:
        run(params.get_src(), params.get_dst(), params.is_force(), True)
        result = {"result": 1, "errorMessage": "", "data": {"body": 200}}
    except Exception as e:
        result = {"result": 0, "errorMessage": str(e)}
    return result


@router.post("/v1/download")
async def download(params: DownloadParams):
    src_path = params.get_path()
    logger.info(f"param src_path :: {src_path}")
    try:
        # dir 이면 zip 으로 압축함
        if os.path.isdir(src_path):
            os.chdir(src_path)  # 압축 파일 생성할 폴더로 working directory 를 이동시킨다
            byte_io = BytesIO()

            zip_file = zipfile.ZipFile(byte_io, "w")
            for (path, dir, files) in os.walk(src_path):
                for file in files:
                    logger.info(f"Adding file :: {file}")
                    # 상대경로를 활용하여 압축한다. (os.path.relpath)
                    zip_file.write(
                        os.path.join(os.path.relpath(path, src_path), file), compress_type=zipfile.ZIP_DEFLATED
                    )

            zip_file.close()
            # zip 파일을 읽도록 주소 변경
            decode_data = base64.b64encode(byte_io.getvalue()).decode()
        else:
            read_file = open(src_path, "rb").read()
            decode_data = base64.b64encode(read_file).decode()

        logger.info(f"decode_data :: {decode_data[:20]} ..")
        result = {"result": 1, "errorMessage": "", "data": {"body": decode_data}}
    except Exception as e:
        result = {"result": 0, "errorMessage": str(e)}
    return result


@router.post("/v1/user")
async def create_user_dir(params: UserParams):
    target_path = params.get_path()
    logger.info(f"param target_path :: {target_path}")
    dirs = ["favorite", "upload", "purchase"]
    try:
        # 세개의 디렉토리 미리 생성
        for dir in dirs:
            os.makedirs(f"{target_path}/{dir}")
        result = {"result": 1, "errorMessage": "", "data": "success"}
    except Exception as e:
        logger.error(e)
        result = {"result": 0, "errorMessage": str(e)}
    return result


def is_dir(src_path):
    return os.path.isdir(
        os.path.join(settings.MYDISK_ROOT_DIR, src_path.lstrip("/") if src_path.startswith("/") else src_path)
    )


def run(src_path, dst_path, is_force, is_copy):
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)

    if os.path.exists(dst_path):
        if is_force:
            shutil.rmtree(dst_path)
        else:
            raise Exception("alreay exist")

    if os.path.isfile(src_path):
        os.link(src_path, dst_path)
    else:
        shutil.copytree(
            src=src_path,
            dst=dst_path,
            dirs_exist_ok=is_force,
            copy_function=os.link if not is_copy else shutil.copy2,
        )


async def get_admin_token() -> None:
    res = await mydisk.generate_admin_token(
        username=settings.MYDISK_INFO.admin_username,
        password=settings.MYDISK_INFO.admin_password,
        scope=settings.MYDISK_INFO.scope,
        client_id=settings.MYDISK_INFO.client_id,
        client_secret=settings.MYDISK_INFO.client_secret,
    )

    return res.get("data").get("access_token")
