from fastapi import APIRouter

from batch_service.routes.v1 import temp

router = APIRouter()

router.include_router(temp.router)
