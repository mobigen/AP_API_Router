import json
import logging
import requests

from pydantic import BaseModel
from fastapi import APIRouter
from starlette.responses import JSONResponse

from login_service.app.common.config import settings

logger = logging.getLogger()
router = APIRouter()


@router.get("/cmp/v2/projectList")
async def get_project_list() -> JSONResponse:
    try:
        url = settings.CMP_INFO.CMP_API_BASE_URL
        res = requests.get(
            url=f"{url}/orgs/manage/all?size=100&page=0",
            verify=False
        )
        data = res.json()
        logger.info(data)
        project_list = data["items"]
        admin_header = get_admin_header()
        for project in project_list :
            project_id = project["id"]
            project["detail"] = get_project_detail(admin_header, project_id)

        return JSONResponse(
            status_code=200,
            content={"result": 1, "errorMessage": "", "data": project_list}
        )
    except Exception as e:
        return result_error(e)


def get_project_detail(admin_header: dict, project_id: str) -> JSONResponse:
    try:
        url = settings.CMP_INFO.CMP_API_BASE_URL
        res = requests.get(
            url=f"{url}/orgs/{project_id}/users",
            headers=admin_header,
            verify=False
        )
        logger.info(res.json())
        return res.json()["items"]
    except Exception as e:
        return result_error(e)


def get_admin_header():
    try:
        url = settings.CMP_INFO.CMP_API_BASE_URL
        cmp_id = settings.CMP_INFO.CMP_ID
        cmp_pass = settings.CMP_INFO.CMP_PASS
        res = requests.post(
            url=f"{url}/adminLogin?email={cmp_id}&password={cmp_pass}",
            verify=False
        )
        logger.info(res.json())
        access_token = res.json()["access_token"]
        header = {'X-HEADER-TOKEN': access_token}
        return header
    except Exception as e:
        raise e


def result_error(e):
    logger.error(e, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"result": 0, "errorMessage": str(e)}
    )
