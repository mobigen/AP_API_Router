import logging
from pydantic import BaseModel
from datetime import datetime
from fastapi import APIRouter, Request, Depends, UploadFile
from starlette.responses import JSONResponse, FileResponse

from common_service.app.database.conn import db
from libs.database.connector import Executor

from app.common.const import AttachFileTable, ATTACH_BASE_DIR


class AttachFileInfo(BaseModel):
    link: str
    file_size: int
    file_ext: str
    file_type: str
    file_name: str

    class Config:
        extra = "forbid"  # 추가 인자는 허용하지 않음


logger = logging.getLogger()
router = APIRouter()


@router.post("/file-upload")
async def file_upload(file: UploadFile, session: Executor = Depends(db.get_db)):
    try:
        data = await file.read()
        cur_time = datetime.today().strftime("%Y%m%d%H%M%S%f")
        file_name = file.filename
        link = f"{ATTACH_BASE_DIR}/{cur_time}"

        file_info = AttachFileInfo(
            link=link,
            file_name=file_name,
            file_ext=file_name.split(".")[-1],
            file_size=file.size,
            file_type=file.content_type,
        )

        logger.info("file Info")
        logger.info(file_info)

        query = AttachFileTable.get_execute_query("insert", file_info.dict())
        session.execute(**query)

        with open(f"{link}", "wb") as fp:
            fp.write(data)

        return JSONResponse(
            status_code=200,
            content={
                "result": 1,
                "errorMessage": "",
                "data": {"body": file_info.dict()}
            }
        )
    except Exception as e:
        logger.info(e)
        return JSONResponse(status_code=200, content={"result": 0, "errorMessage": str(e)})


@router.get("/file-download/{category}/{file}")
def file_download(category: str, file: str, session: Executor = Depends(db.get_db)):
    try:
        link = f"/{category}/{file}"
        file_attach_info = session.query(**AttachFileTable.get_select_query(link)).first()

        file_name = file_attach_info["file_name"]
        file_type = file_attach_info["file_type"]

        return FileResponse(link, media_type=file_type, filename=file_name)

    except Exception as e:
        logger.info(e)
        return JSONResponse(status_code=200, content={"result": 0, "errorMessage": str(e)})

