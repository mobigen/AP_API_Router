from fastapi import APIRouter
from starlette.responses import JSONResponse


router = APIRouter()


@router.get("/insert_email")
async def insert_email():

    return JSONResponse(status_code=200, content="ok")
