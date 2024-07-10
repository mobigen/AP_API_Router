import json
import logging
import requests

from pydantic import BaseModel
from fastapi import APIRouter
from starlette.responses import JSONResponse

from login_service.app.common.const import json_headers
from login_service.app.common.config import settings

logger = logging.getLogger()
router = APIRouter()


class UserInfoWrap(BaseModel):
    class UserInfo(BaseModel):
        user_id: str
        email: str
        name: str

    data: UserInfo


@router.get("/cmp/v2/projectList")
async def get_project_list() -> JSONResponse:
    try:
        url = settings.CMP_INFO.CMP_API_BASE_URL
        params = {
            "page": 0,
            "size": 200
        }
        res = requests.get(
            url=f"{url}/orgs/manage/all",
            params=params,
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


@router.get("/cmp/v2/projectUser")
async def get_project_user() -> JSONResponse:
    try:
        admin_header = get_admin_header()
        url = settings.CMP_INFO.CMP_API_BASE_URL

        params = {
            "token": admin_header["X-HEADER-TOKEN"],
            "page": 0,
            "size": 200
        }
        res = requests.get(
            url=f"{url}/users",
            params=params,
            verify=False
        )
        logger.info(res.json())
        return JSONResponse(
            status_code=200,
            content={"result": 1, "errorMessage": "", "data": res.json()["content"]}
        )
    except Exception as e:
        return result_error(e)


@router.post("/cmp/v2/createUser")
async def create_project_user(params: UserInfoWrap) -> JSONResponse:
    try:
        url = settings.CMP_INFO.CMP_API_BASE_URL
        param = params.data

        payload = {
            "userId": param.user_id,
            "email": param.email,
            "name": param.name,
            "userRole": "USER"
        }
        res = requests.post(
            url=f"{url}/users",
            headers=json_headers,
            data=json.dumps(payload),
            verify=False
        )
        logger.info(res)
        return JSONResponse(
            status_code=200,
            content={"result": 1, "errorMessage": "", "data": "success"}
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
        params = {
            "email": settings.CMP_INFO.CMP_ID,
            "password": settings.CMP_INFO.CMP_PASS
        }
        res = requests.post(
            url=f"{url}/adminLogin",
            params=params,
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