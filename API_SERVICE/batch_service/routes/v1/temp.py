from fastapi import APIRouter
from starlette.responses import JSONResponse


router = APIRouter()


@router.get("/")
async def healthcheck():
    return JSONResponse(status_code=200, content="ok")
